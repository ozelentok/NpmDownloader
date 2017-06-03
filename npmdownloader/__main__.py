import argparse

from .multipackagedownloader import MultiPackageDownloader
from .logger import log

def main():
    parser = argparse.ArgumentParser(description='Download npm packages including dependencies')
    parser.add_argument(
        '-f', '--packages-file', required=True,
        help='File with packages to download, seperated by newlines')
    parser.add_argument(
        '-o', '--download-dir', required=True,
        help='Output directory to download packages to')
    parser.add_argument(
        '-c', '--workers-count', required=True, type=int,
        help='Number of worker processes to spawn')
    args = parser.parse_args()

    downloader = MultiPackageDownloader(args.packages_file, args.download_dir, args.workers_count)
    log.info('Multi Download Started')
    downloader.start()
    downloader.wait()
    log.info('Multi Download Finished')

if __name__ == '__main__':
    main()
