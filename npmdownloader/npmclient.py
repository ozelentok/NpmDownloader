import os
import urllib.request
import json
import shutil
import fasteners

from . import utils

class NpmClient:

    @classmethod
    def _get_json(cls, url: str):
        response = urllib.request.urlopen(url).read()
        return json.loads(response.decode('utf-8'))

    @classmethod
    def get_package_latest_version(cls, name: str):
        return cls.get_registry_package_info(name, version='latest')['version']

    @classmethod
    def get_package_versions(cls, name: str):
        content = cls._get_json(utils.build_all_versions_url(name))
        return list(content['versions'].keys())

    @classmethod
    def get_registry_package_info(cls, name: str, version: str):
        #NPM Site does not allow /{version} for scoped packages
        if not utils.is_scoped(name):
            return cls._get_json(utils.build_version_url(name, version))
        content = cls._get_json(utils.build_all_versions_url(name))
        return content['versions'][content['dist-tags'][version]]

    @classmethod
    def download_tar_ball_of(cls, name: str, version: str, download_dir: str):
        file_name = utils.build_filename(name, version)
        url = utils.build_tarball_url(name, version)
        parent_dir = os.path.join(download_dir, name)
        os.makedirs(parent_dir, exist_ok=True)
        file_path = os.path.join(parent_dir, file_name)
        if os.path.exists(file_path):
            return (file_path, False)

        file_lock = fasteners.InterProcessLock(file_path)
        with fasteners.try_lock(file_lock) as got_file_lock:
            if not got_file_lock:
                return (file_path, False)

            with urllib.request.urlopen(url) as download_stream:
                with open(file_path, 'wb') as file_stream:
                    shutil.copyfileobj(download_stream, file_stream)
            return (file_path, True)

    @classmethod
    def get_latest_dependencies_version(cls, dependencies: dict) -> dict:
        dependencies_versions = {}
        for package, version in dependencies.items():
            dependencies_versions[package] = cls.get_latest_satisfying_version(package, version)
        return dependencies_versions

    @classmethod
    def get_latest_satisfying_version(cls, name, version) -> str:
        versions = cls.get_package_versions(name)
        return utils.find_lastest_satisfying_version(versions, version)
