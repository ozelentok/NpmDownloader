import argparse
import queue
import re
import api

PACKAGE_WITH_VERSION_PATTERN = re.compile(r'^(.+)@(.+)$')

def parse_args():
    parser = argparse.ArgumentParser(description='Download npm packages including dependencies')
    parser.add_argument('-f', '--packages-file', 
                        required=True, help='File with packages to download, seperated by newlines')
    parser.add_argument('-o', '--output-dir', 
                        required=True, help='Output directory to download packages to')
    return parser.parse_args()

def create_package_queue(packages_file):
    package_queue = queue.Queue()
    with open(packages_file, 'r') as input_file:
        for line in input_file:
            package = line.strip()
            version = None
            pattern_match = PACKAGE_WITH_VERSION_PATTERN.match(package)
            if pattern_match:
                package = pattern_match.group(1)
                version = pattern_match.group(2)
            package_queue.put((package, version))
    return package_queue

def main():
    args = parse_args()
    package_queue = create_package_queue(args.packages_file)
    while not package_queue.empty():
        package = package_queue.get()
        dependencies = api.download_package(package[0], package[1], args.output_dir)
        for sub_package, sub_package_version in dependencies.items():
            package_queue.put((sub_package, sub_package_version))
        package_queue.task_done()

if __name__ == '__main__':
    main()
