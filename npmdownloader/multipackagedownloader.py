import multiprocessing
import re

from .packagedownloader import NpmPackageDownloader

class MultiPackageDownloader:

    _PACKAGE_WITH_VERSION_PATTERN = re.compile(r'^(.+)@(.+)$')

    def __init__(self, package_list_file_path: str, download_dir: str, num_of_workers: int):
        self._download_dir = download_dir
        self._num_of_workers = num_of_workers
        self._workers = []
        self._package_groups = list(self._group_packages(package_list_file_path))

    def _group_packages(self, package_list_file_path: str):
        with open(package_list_file_path, 'r') as input_file:
            packages = [line.strip() for line in input_file]

        package_groups = [[] for _ in range(self._num_of_workers)]
        for i, package in enumerate(packages):
            package_groups[i % self._num_of_workers].append(package)
        for group in package_groups:
            yield [self._parse_package(package) for package in group]

    def _parse_package(self, package):
        version = None
        pattern_match = self._PACKAGE_WITH_VERSION_PATTERN.match(package)
        if pattern_match:
            package = pattern_match.group(1)
            version = pattern_match.group(2)
        return (package, version)

    def start(self):
        self._workers = []
        for i in range(self._num_of_workers):
            worker = multiprocessing.Process(
                target=self._packages_downloader,
                args=(self._package_groups[i], self._download_dir))
            worker.start()
            self._workers.append(worker)

    def wait(self):
        for i in self._workers:
            i.join()

    @staticmethod
    def _packages_downloader(packages, download_dir):
        package_downloader = NpmPackageDownloader(download_dir)
        package_downloader.download_multiple(packages)
