import tarfile
import re
import codecs
import json
import queue

from npm_api import NpmRegistryClient

class NpmPackage:

    PACKAGE_JSON_PATH_PATTERN = re.compile(r'^[^\/]+\/package\.json$')

    __slots__ = ('name', 'version', 'file_path')

    def __init__(self, name: str, version: str, file_path: str):
        self.name = name
        self.version = version
        self.file_path = file_path

    def get_dependencies(self) -> dict:
        package_info = self.get_package_json()
        if 'dependencies' not in package_info:
            return {}
        return package_info['dependencies']

    def get_package_json(self) -> dict:
        with tarfile.open(self.file_path, 'r:gz') as tar_file:
            for internal_path in tar_file.getnames():
                if not NpmPackage.PACKAGE_JSON_PATH_PATTERN.match(internal_path):
                    continue
                member = tar_file.getmember(internal_path)
                with tar_file.extractfile(member) as file_stream:
                    return NpmPackage.parse_package_json(file_stream)
        return {}

    @staticmethod
    def parse_package_json(file_stream):
        data = file_stream.read()
        if data.startswith(codecs.BOM_UTF8):
            encoded_data = data.decode('utf-8-sig')
        else:
            encoded_data = data.decode('utf-8')
        return json.loads(encoded_data)

class NpmPackageDownloader:

    def __init__(self, download_dir: str):
        self._download_dir = download_dir

    def download_single_package(self, name: str, version: str) -> (NpmPackage, bool):
        if version is None:
            version = NpmRegistryClient.get_package_latest_version(name)
        file_path, was_downloaded = NpmRegistryClient.download_tar_ball_of(name, version, self._download_dir)
        package_info = NpmPackage(name=name, version=version, file_path=file_path)
        return package_info, was_downloaded

    def download_package(self, name: str, version: str):
        package_queue = queue.Queue()
        if version is None:
            version = NpmRegistryClient.get_package_latest_version(name)
        package_queue.put(name, version)
        while not package_queue.empty():
            current_item = package_queue.get()
            package_queue.task_done()
            package, was_downloaded = self.download_single_package(*current_item)
            if not was_downloaded:
                continue
            dependencies = NpmRegistryClient.get_latest_dependencies_version(package.get_dependencies())
            for sub_package, sub_package_version in dependencies.items():
                package_queue.put((sub_package, sub_package_version))
