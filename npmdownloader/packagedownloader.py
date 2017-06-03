import collections
import asyncio
from typing import List

from .npmclient import NpmClient
from .npmpackage import NpmPackage
from . import utils

class NpmPackageDownloader:

    def __init__(self, download_dir: str):
        self._client = NpmClient()
        self._download_dir = download_dir

    async def download_single_package(self, name: str, version: str=None) -> (NpmPackage, bool):
        if version is None:
            version = await self._client.get_package_latest_version(name)
        file_path, was_downloaded = await self._client.download_tar_ball_of(name, version, self._download_dir)
        package_info = NpmPackage(name=name, version=version, file_path=file_path)
        return package_info, was_downloaded

    async def download_packages(self, packages):
        package_queue = collections.deque()
        while packages:
            results = await asyncio.gather([self.download_single_package(n, v) for n, v in packages])
            for package, was_downloaded in results:
                if not was_downloaded:
                    continue
                dependencies = await self._client.get_latest_dependencies_version(package.get_dependencies())
                for sub_package, sub_package_version in dependencies.items():
                    package_queue.appendleft((sub_package, sub_package_version))
            packages = utils.multi_pop(package_queue)

    def download_multiple(self, packages: List):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.download_packages(packages))

    def download(self, name: str, version: str=None):
        self.download_multiple([name, version])
