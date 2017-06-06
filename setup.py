import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='npmdownloader',
    packages=['npmdownloader'],
    version='1.1.1',
    description='NPM Package Downloader',
    long_description=read('README.rst'),
    author='Oz Elentok',
    author_email='oz.elen@gmail.com',
    url='https://github.com/ozelentok/npmdownloader',
    download_url='https://github.com/ozelentok/npmdownloader/tarball/1.1.1',
    keywords='npm nodejs sinopia verdaccio offline',
    install_requires=['node-semver', 'fasteners', 'aiohttp', 'aiofiles'],
    license='MIT',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development',
        'Topic :: System :: Software Distribution',
    ]
)
