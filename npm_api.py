import os
import urllib.request
import json
import shutil

import name_utils
import uri_utils

NPM_REGISTRY_URL = 'https://registry.npmjs.org'

def build_filename(name, version):
    return '{}-{}.tgz'.format(name_utils.unscope_name(name), version)

def build_url(name, version=None):
    if uri_utils.is_uri(version):
        return version
    if not version:
        return '{}/{}/'.format(NPM_REGISTRY_URL, name.replace('%2f', '/'))
    return '{}/{}/-/{}'.format(NPM_REGISTRY_URL, name.replace('%2f', '/'), build_filename(name, version))

def get_json(url):
    response = urllib.request.urlopen(url).read()
    return json.loads(response.decode('utf-8'))

def get_versions_of(name):
    content = get_json(build_url(name))
    return list(content['versions'].keys())

def get_latest_of(name):
    #NPM Site does not allow /latest for scoped packages
    if not name_utils.is_scoped(name):
        return get_json('{}latest'.format(build_url(name)))
    content = get_json('{}/{}'.format(NPM_REGISTRY_URL, name))
    return content['versions'][content['dist-tags']['latest']]

def get_latest_version_of(name):
    content = get_latest_of(name)
    return content['version']

def download_tar_ball_of(name, version, download_dir):
    file_name = build_filename(name, version)
    url = build_url(name, version)
    parent_dir = os.path.join(download_dir, name)
    os.makedirs(parent_dir, exist_ok=True)
    download_stream = urllib.request.urlopen(url)
    print('Started download of: {}'.format(file_name))
    file_path = os.path.join(parent_dir, file_name)
    with urllib.request.urlopen(url) as download_stream:
        with open(file_path, 'wb') as file_stream:
            shutil.copyfileobj(download_stream, file_stream)
    print('Finished download of: {}'.format(file_name))
    return file_path
