NPM Downloader
==============
Download packages from NPM for private npm servers such as verdaccio and sinopia

- Python 3.5+ only

Installation
------------

Install using pip:

.. code:: bash

  $ pip install npmdownloader

Usage
-----
Downloading using the CLI:
 
.. code:: bash

    $ python -m npmdownloader -f [PACKAGE_FILE_LIST] -o [DOWNLOAD_DIR] -c [NUM_OF_WORKER_PROCESSES]

Downloading a package using code:

.. code:: python

  from npmdownloader import NpmPackageDownloader

  downloader = NpmPackageDownloader('out_dir')
  # Download a package and its depedencies as tarballs
  # if a package tarball already exists, the download will be skipped
  downloader.download('react', version='15.4.1')

Downloading multiple packages using code:

.. code:: python

  from npmdownloader import MultiPackageDownloader

  downloader = MultiPackageDownloader('packages_list.txt', 'out_dir', workers_count=4)
