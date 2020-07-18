import os
from typing import Dict, List, Any, Tuple, Optional
import aiohttp
import aiofiles
import fasteners

from . import utils
from .logger import log


class NpmClient:
    async def __aenter__(self) -> 'NpmClient':
        self._session = aiohttp.ClientSession(raise_for_status=True)
        return self

    async def __aexit__(self, *args) -> None:
        await self._session.close()

    async def _get_json(self, url: str) -> Dict:
        try:
            log.debug('GET %s', url)
            async with self._session.get(url) as response:
                return await response.json()
        except Exception:
            log.exception('Failed to get JSON from %s', url)
            raise

    async def get_package_latest_version(self, name: str) -> str:
        return (await self.get_registry_package_info(name, 'latest'))['version']

    async def get_package_versions(self, name: str) -> List[str]:
        content = await self._get_json(utils.build_all_versions_url(name))
        return list(content['versions'].keys())

    async def get_registry_package_info(self, name: str, version: str) -> Dict[str, Any]:
        # NPM Site does not allow /{version} for scoped packages
        if not utils.is_scoped(name):
            return await self._get_json(utils.build_version_url(name, version))
        content = await self._get_json(utils.build_all_versions_url(name))
        return content['versions'][content['dist-tags'][version]]

    async def download_tar_ball_of(self, name: str, version: str, download_dir: str) -> Tuple[str, bool]:
        file_name = utils.build_filename(name, version)
        url = utils.build_tarball_url(name, version)
        parent_dir = os.path.join(download_dir, name)
        os.makedirs(parent_dir, exist_ok=True)
        file_path = os.path.join(parent_dir, file_name)
        if os.path.exists(file_path):
            return file_path, False

        file_lock = fasteners.InterProcessLock(file_path)
        with fasteners.try_lock(file_lock) as got_file_lock:
            if not got_file_lock:
                return file_path, False

            async with self._session.get(url) as response:
                async with aiofiles.open(file_path, 'wb') as file_stream:
                    await utils.copyfileobj(response.content, file_stream)
            return file_path, True

    async def get_latest_dependencies_version(self, dependencies: Dict[str, str]) -> Dict[str, str]:
        dependencies_versions = {}
        for package, version in dependencies.items():
            try:
                dependencies_versions[package] = await self.get_latest_satisfying_version(package, version)
            except Exception:
                log.exception('Failed getting %s-%s latest version', package, version)
        return dependencies_versions

    async def get_latest_satisfying_version(self, name, version) -> str:
        versions = await self.get_package_versions(name)
        return utils.find_lastest_satisfying_version(versions, version)
