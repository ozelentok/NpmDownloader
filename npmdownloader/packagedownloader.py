import collections
import asyncio
from typing import List, Dict

from .npmclient import NpmClient
from .npmpackage import NpmPackage
from .logger import log
from . import utils

class NpmPackageDownloader:

    def __init__(self, download_dir: str, max_tasks: int=10):
        self._client = NpmClient()
        self._download_dir = download_dir
        self._max_tasks = max_tasks

    async def _download_single_package(self, name: str, version: str=None) -> (NpmPackage, bool):
        try:
            name = utils.normalize_package(name)
            if version is None:
                log.info('Downloading %s', name)
                version = await self._client.get_package_latest_version(name)
            else:
                log.info('Downloading %s@%s', name, version)
            file_path, was_downloaded = await self._client.download_tar_ball_of(name, version, self._download_dir)
            package_info = NpmPackage(name=name, version=version, file_path=file_path)
            log.info('Downloaded %s@%s', name, version)
            return package_info, was_downloaded
        except:
            log.error('Error downloading %s', name)
            return (None, False)

    async def _get_package_latest_dependencies(self, package: NpmPackage) -> Dict[str, str]:
        try:
            required_dependencies = await package.get_dependencies()
            normalized_dependencies = {utils.normalize_package(k): v for k, v in required_dependencies.items()}
            return await self._client.get_latest_dependencies_version(normalized_dependencies)
        except:
            log.error('Error getting %s dependencies', package.name)
            return {}

    async def download_packages(self, packages: List[NpmPackage]):
        self._client.connect()
        package_queue = collections.deque(packages)

        current_packages = utils.multi_pop(package_queue, self._max_tasks)
        tasks = [self._download_single_package(n, v) for n, v in current_packages]
        while tasks:
            tasks_done, tasks_pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in tasks_done:
                package, was_downloaded = task.result()
                if not was_downloaded:
                    continue
                dependencies = await self._get_package_latest_dependencies(package)
                for sub_package, sub_package_version in dependencies.items():
                    package_queue.appendleft((sub_package, sub_package_version))
            additional_packages = utils.multi_pop(package_queue, min(len(tasks_done), self._max_tasks))
            tasks_pending.update([self._download_single_package(n, v) for n, v in additional_packages])
            tasks = tasks_pending
        self._client.close()

    def download_multiple(self, packages: List[NpmPackage]):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.download_packages(packages))

    def download(self, name: str, version: str=None):
        self.download_multiple([(name, version)])
