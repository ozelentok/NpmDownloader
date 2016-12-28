import argparse

from multipackagedownloader import MultiPackageDownloader

def parse_args():
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
    return parser.parse_args()

def main():
    args = parse_args()
    downloader = MultiPackageDownloader(args.packages_file, args.download_dir, args.workers_count)
    print('multi package downloader starting')
    downloader.start()
    downloader.wait()
    print('multi package downloader finished')


if __name__ == '__main__':
    main()
