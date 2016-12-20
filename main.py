import argparse
import multiprocessing
import re
import api
import utils

PACKAGE_WITH_VERSION_PATTERN = re.compile(r'^(.+)@(.+)$')
NUM_OF_WORKERS = 4

def parse_args():
    parser = argparse.ArgumentParser(description='Download npm packages including dependencies')
    parser.add_argument('-f', '--packages-file',
                        required=True, help='File with packages to download, seperated by newlines')
    parser.add_argument('-o', '--output-dir',
                        required=True, help='Output directory to download packages to')
    return parser.parse_args()

def create_package_queue(packages_file):
    package_queue = multiprocessing.JoinableQueue()
    with open(packages_file, 'r') as input_file:
        for line in input_file:
            package = utils.normalize_package(line.strip())
            version = None
            pattern_match = PACKAGE_WITH_VERSION_PATTERN.match(package)
            if pattern_match:
                package = pattern_match.group(1)
                version = pattern_match.group(2)
            package_queue.put((package, version))
    return package_queue

def start_package_downloaders(package_queue, output_dir):
    workers = []
    for _ in range(NUM_OF_WORKERS):
        worker = multiprocessing.Process(target=packages_downloader, args=(package_queue, output_dir))
        worker.start()
        workers.append(worker)
    return workers

def stop_package_downloaders(package_queue, workers):
    for i in range(len(workers)):
        package_queue.put(None)
    for i in workers:
        i.join()

def main():
    args = parse_args()
    package_queue = create_package_queue(args.packages_file)
    workers = start_package_downloaders(package_queue, args.output_dir)
    package_queue.join()
    stop_package_downloaders(package_queue, workers)

def packages_downloader(package_queue, output_dir):
    while True:
        package = package_queue.get()
        try:
            if package is None:
                break
            print('Downloading {}'.format(package[0]))
            dependencies = api.download_package(package[0], package[1], output_dir)
            for sub_package, sub_package_version in dependencies.items():
                package_queue.put((sub_package, sub_package_version))
            print('Finished {}'.format(package[0]))
        except Exception as e:
            print('Failed to download {}\nException: {}'.format(package[0], e))
        package_queue.task_done()

if __name__ == '__main__':
    main()
