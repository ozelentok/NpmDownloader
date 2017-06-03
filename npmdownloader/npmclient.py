import os
import shutil
import aiohttp
import aiofiles

from . import utils

class NpmClient:

    def __init__(self):
        self._session = aiohttp.ClientSession(raise_for_status=True)
        self._files_open = set()

    async def _get_json(self, url: str):
        async with self._session.get(url) as response:
            return await response.json()

    async def get_package_latest_version(self, name: str):
        return await self.get_registry_package_info(name, version='latest')['version']

    async def get_package_versions(self, name: str):
        content = await self._get_json(utils.build_all_versions_url(name))
        return list(content['versions'].keys())

    async def get_registry_package_info(self, name: str, version: str):
        #NPM Site does not allow /{version} for scoped packages
        if not utils.is_scoped(name):
            return await self._get_json(utils.build_version_url(name, version))
        content = await self._get_json(utils.build_all_versions_url(name))
        return content['versions'][content['dist-tags'][version]]

    async def download_tar_ball_of(self, name: str, version: str, download_dir: str):
        file_name = utils.build_filename(name, version)
        url = utils.build_tarball_url(name, version)
        parent_dir = os.path.join(download_dir, name)
        os.makedirs(parent_dir, exist_ok=True)
        file_path = os.path.join(parent_dir, file_name)
        if file_path in self._files_open or os.path.exists(file_path):
            return (file_path, False)
        self._files_open.add(file_path)

        async with self._session.get(url) as response:
            async with aiofiles.open(file_path, 'wb') as file_stream:
                await utils.copyfileobj(response, file_stream)
        return (file_path, True)

    async def get_latest_dependencies_version(self, dependencies: dict) -> dict:
        dependencies_versions = {}
        for package, version in dependencies.items():
            dependencies_versions[package] = await self.get_latest_satisfying_version(package, version)
        return dependencies_versions

    async def get_latest_satisfying_version(self, name, version) -> str:
        versions = await self.get_package_versions(name)
        return utils.find_lastest_satisfying_version(versions, version)
