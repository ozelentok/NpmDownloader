import queue

from .npmclient import NpmClient
from .npmpackage import NpmPackage

class NpmPackageDownloader:

    def __init__(self, download_dir: str):
        self._download_dir = download_dir

    def download_single_package(self, name: str, version: str=None) -> (NpmPackage, bool):
        if version is None:
            version = NpmClient.get_package_latest_version(name)
        file_path, was_downloaded = NpmClient.download_tar_ball_of(name, version, self._download_dir)
        package_info = NpmPackage(name=name, version=version, file_path=file_path)
        return package_info, was_downloaded

    def download_package(self, name: str, version: str=None):
        package_queue = queue.Queue()
        if version is None:
            version = NpmClient.get_package_latest_version(name)
        package_queue.put(name, version)
        while not package_queue.empty():
            current_item = package_queue.get()
            package_queue.task_done()
            package, was_downloaded = self.download_single_package(*current_item)
            if not was_downloaded:
                continue
            dependencies = NpmClient.get_latest_dependencies_version(package.get_dependencies())
            for sub_package, sub_package_version in dependencies.items():
                package_queue.put((sub_package, sub_package_version))
