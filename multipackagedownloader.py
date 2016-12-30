import multiprocessing
import re
import sys

from .npmclient import NpmClient
from .packagedownloader import NpmPackageDownloader
from . import utils

class MultiPackageDownloader:

    _PACKAGE_WITH_VERSION_PATTERN = re.compile(r'^(.+)@(.+)$')

    def __init__(self, package_list_file_path: str, download_dir: str, num_of_workers: int):
        self._package_queue = multiprocessing.JoinableQueue()
        self._download_dir = download_dir
        self._num_of_workers = num_of_workers
        self._workers = []

        self._fill_package_queue(package_list_file_path)

    def _fill_package_queue(self, package_list_file_path: str):
        with open(package_list_file_path, 'r') as input_file:
            for line in input_file:
                package = utils.normalize_package(line.strip())
                version = None
                pattern_match = MultiPackageDownloader._PACKAGE_WITH_VERSION_PATTERN.match(package)
                if pattern_match:
                    package = pattern_match.group(1)
                    version = pattern_match.group(2)
                self._package_queue.put((package, version))

    def start(self):
        self._workers = []
        for _ in range(self._num_of_workers):
            worker = multiprocessing.Process(
                target=MultiPackageDownloader._packages_downloader,
                args=(self._package_queue, self._download_dir))
            worker.start()
            self._workers.append(worker)

    def wait(self):
        self._package_queue.join()
        for i in range(self._num_of_workers):
            self._package_queue.put(None)
        for i in self._workers:
            i.join()

    @staticmethod
    def _packages_downloader(package_queue, download_dir):
        package_downloader = NpmPackageDownloader(download_dir)
        while True:
            package = package_queue.get()
            try:
                if package is None:
                    break
                print('Downloading {}'.format(package[0]))
                package_info, was_downloaded = package_downloader.download_single_package(package[0], package[1])
                if not was_downloaded:
                    continue
                dependencies = NpmClient.get_latest_dependencies_version(package_info.get_dependencies())
                for sub_package, sub_package_version in dependencies.items():
                    package_queue.put((sub_package, sub_package_version))
                print('Finished {}'.format(package[0]))
            except Exception as e:
                print('Failed to download {}\nException: {}'.format(package[0], e), file=sys.stderr)
            finally:
                package_queue.task_done()
