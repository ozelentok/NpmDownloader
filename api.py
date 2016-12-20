import tarfile
import re
import codecs
import json

import npm_api
import version_utils

PACKAGE_JSON_PATH_PATTERN = re.compile(r'^[^\/]+\/package\.json$')

def download_package(name, version, download_dir):
    if version is None:
        version = add_version_for(name)
    file_path, was_downloaded = npm_api.download_tar_ball_of(name, version, download_dir)
    if not was_downloaded:
        return {}
    dependencies = get_dependencies_from_tar_gz(file_path)
    return get_latest_dependencies(dependencies)

def add_version_for(name):
    return npm_api.get_registry_package_info(name)['version']

def get_dependencies_from_tar_gz(file_path):
    package_info = get_package_json_from_tar_gz(file_path)
    if 'dependencies' not in package_info:
        return {}
    return package_info['dependencies']

def get_package_json_from_tar_gz(file_path):
    with tarfile.open(file_path, 'r:gz') as tar_file:
        for internal_path in tar_file.getnames():
            if not PACKAGE_JSON_PATH_PATTERN.match(internal_path):
                continue
            member = tar_file.getmember(internal_path)
            with tar_file.extractfile(member) as file_stream:
                return parse_package_json(file_stream)
    return {}

def parse_package_json(file_stream):
    data = file_stream.read()
    if data.startswith(codecs.BOM_UTF8):
        encoded_data = data.decode('utf-8-sig')
    else:
        encoded_data = data.decode('utf-8')
    return json.loads(encoded_data)

def get_latest_dependencies(dependencies):
    dependencies_versions = {}
    for package, version in dependencies.items():
        print('Getting {}@{} latest satisfying version'.format(package, version))
        dependencies_versions[package] = get_latest_satisfying_version(package, version)
    return dependencies_versions

def get_latest_satisfying_version(name, version):
    versions = npm_api.get_versions_of(name)
    return version_utils.get_lastest_satisfying_version(versions, version)
