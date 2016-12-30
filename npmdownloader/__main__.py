import argparse

from .multipackagedownloader import MultiPackageDownloader

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
    print('Package downloader started')
    downloader.start()
    downloader.wait()
    print('Package downloader finished')

if __name__ == '__main__':
    main()
