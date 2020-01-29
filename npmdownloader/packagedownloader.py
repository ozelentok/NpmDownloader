import asyncio
from typing import List, Dict, Tuple, Optional, Deque, Awaitable, Any

from .npmclient import NpmClient
from .npmpackage import NpmPackage
from .logger import log
from . import utils


class NpmPackageDownloader:
    def __init__(self, download_dir: str, max_tasks: int = 10):
        self._download_dir = download_dir
        self._max_tasks = max_tasks
        self._client = NpmClient()

    async def _download_single_package(self, name: str, version: Optional[str]) -> Optional[NpmPackage]:
        try:
            name = utils.normalize_package(name)
            if version is None:
                log.info('Downloading %s', name)
                version = await self._client.get_package_latest_version(name)
            else:
                log.info('Downloading %s@%s', name, version)
            file_path, was_downloaded = await self._client.download_tar_ball_of(name, version, self._download_dir)
            package_info = NpmPackage(name=name, version=version, file_path=file_path)
            if was_downloaded:
                log.info('Downloaded %s@%s', name, version)
            else:
                log.info('Skipping %s@%s, already downloaded', name, version)
            return package_info
        except Exception:
            log.error('Error downloading %s', name)
            return None

    async def _get_package_latest_dependencies(self, package: NpmPackage) -> Dict[str, str]:
        try:
            required_dependencies = await package.get_dependencies()
            normalized_dependencies = {utils.normalize_package(k): v for k, v in required_dependencies.items()}
            return await self._client.get_latest_dependencies_version(normalized_dependencies)
        except Exception:
            log.error('Error getting %s dependencies', package.name)
            return {}

    async def _download_packages(self, packages: List[Tuple[str, Optional[str]]]):
        package_queue = Deque[Tuple[str, Optional[str]]](packages)

        async with self._client:
            current_packages = utils.multi_pop(package_queue, self._max_tasks)
            tasks: List[Awaitable[Any]] = [asyncio.create_task(self._download_single_package(n, v))
                                           for n, v in current_packages]
            while tasks:
                tasks_done, tasks_pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for task in tasks_done:
                    package_info = task.result()
                    if not package_info:
                        continue
                    dependencies = await self._get_package_latest_dependencies(package_info)
                    for sub_package, sub_package_version in dependencies.items():
                        package_queue.appendleft((sub_package, sub_package_version))
                additional_packages = utils.multi_pop(package_queue, min(len(tasks_done), self._max_tasks))
                tasks_pending.update([asyncio.create_task(self._download_single_package(n, v))
                                      for n, v in additional_packages])
                tasks = list(tasks_pending)

    def download_multiple(self, packages: List[Tuple[str, Optional[str]]]):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._download_packages(packages))

    def download(self, name: str, version: Optional[str] = None):
        self.download_multiple([(name, version)])
