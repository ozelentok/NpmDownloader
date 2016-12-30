from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='npmdownloader',
    packages=['npmdownloader'],
    version='1.0.0a1',
    description='NPM Package Downloader',
    long_description=read('README.rst'),
    author='Oz Elentok',
    author_email='oz.elen@gmail.com',
    url='https://github.com/ozelentok/npmdownloader',
    download_url='https://github.com/ozelentok/npmdownloader/tarball/1.0.1a',
    keywords=['npm', 'nodejs', 'sinopia', 'verdaccio', 'offline'],
    install_requires=['node-semver', 'fasteners'],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development',
        'Topic :: System :: Software Distribution',
    ]
)
