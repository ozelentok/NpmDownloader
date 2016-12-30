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

    $ python -m npmdownloader -f [PACKAGE_LIST] -o [DOWNLOAD_DIR] -c [NUM_OF_WORKER_PROCESS]

Downloading a package from code:

.. code:: python

  from npmdownloader import NpmPackageDownloader

  downloader = NpmPackageDownloader('out_dir')
  #Download package and get depedencies from tarball
  #If the tarball already exists, the download will be skipped
  package_info, was_downloaded = downloader.download_single('react', version='15.4.1')

  #Extract information from the tarball package.json
  package_json = package_info.get_package_json()

  #Extract dependencies dictionary (package_name => version)
  dependencies = package_info.get_dependencies()

Downloading multiple packages from code:

.. code:: python

  from npmdownloader import MultiPackageDownloader

  downloader = MultiPackageDownloader('packages_list.txt', 'out_dir', workers_count=4)
