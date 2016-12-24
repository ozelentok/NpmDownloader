import os
import urllib.request
import json
import shutil
import fasteners

import utils

LOCKS_DIR = 'Locks'

os.makedirs(LOCKS_DIR, exist_ok=True)

def get_json(url):
    response = urllib.request.urlopen(url).read()
    return json.loads(response.decode('utf-8'))

def get_versions_of(name):
    content = get_json(utils.build_all_versions_url(name))
    return list(content['versions'].keys())

def get_registry_package_info(name, version='latest'):
    #NPM Site does not allow /{version} for scoped packages
    if not utils.is_scoped(name):
        return get_json(utils.build_version_url(name, version))
    content = get_json(utils.build_all_versions_url(name))
    return content['versions'][content['dist-tags'][version]]

def download_tar_ball_of(name, version, download_dir):
    file_name = utils.build_filename(name, version)
    url = utils.build_tarball_url(name, version)
    parent_dir = os.path.join(download_dir, name)
    os.makedirs(parent_dir, exist_ok=True)
    file_path = os.path.join(parent_dir, file_name)
    if os.path.exists(file_path):
        return (file_path, False)

    lock_path = os.path.join(LOCKS_DIR, '{}-{}'.format(name, file_name))
    file_lock = fasteners.InterProcessLock(lock_path)
    with fasteners.try_lock(file_lock) as got_file_lock:
        if not got_file_lock:
            return (file_path, False)

        print('Started download of: {}'.format(file_name))
        with urllib.request.urlopen(url) as download_stream:
            with open(file_path, 'wb') as file_stream:
                shutil.copyfileobj(download_stream, file_stream)
        print('Finished download of: {}'.format(file_name))
        return (file_path, True)
