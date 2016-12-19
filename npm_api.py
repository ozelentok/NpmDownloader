import os
import curio
import curio_http
import name_utils
from uri_utils import is_uri

NPM_REGISTRY_URL = 'https://registry.npmjs.org'

def build_filename(name, version):
    return '{}-{}.tgz'.format(name_utils.unscope_name(name), version)

def build_url(name, version=None):
    if is_uri(version):
        return version
    if not version:
        return '{}/{}/'.format(NPM_REGISTRY_URL, name.replace('%2f', '/'))
    return '{}/{}/-/{}'.format(NPM_REGISTRY_URL, name.replace('%2f', '/'), build_filename(name, version))

async def get_json(url):
    async with curio_http.ClientSession() as session:
        response = await session.get(url)
        response.raise_for_status()
        return await response.json()
    #TODO: Check if I need to swallow error here, like the original code

async def get_versions_of(name):
    content = await get_json(build_url(name))
    return list(content['versions'].keys())

async def get_dependencies_of(package, version=None):
    if not version:
        return await get_dependencies_of_latest(package)
    print('Getting dependcies of: {}'.format(package))
    content = await get_json(build_url(package))
    print('Done Getting dependcies of: {}'.format(package))
    version_info = content['versions'][version]
    if 'dependencies' not in version_info:
        return {}
    return version_info['dependencies']

async def get_dependencies_of_latest(name):
    content = await get_latest_of(name)
    return content['dependencies']

async def get_latest_of(name):
    #NPM Site does not allow /latest for scoped packages
    if name_utils.is_scoped(name):
        print('Getting latest of: {}'.format(name))
        content = await get_json('{}/{}'.format(NPM_REGISTRY_URL, name))
        print('Getting latest of: {}'.format(name))
        return content['versions'][content['dist-tags']['latest']]
    return await get_json('{}latest'.format(build_url(name)))

async def get_latest_version_of(name):
    content = await get_latest_of(name)
    return content['version']

async def get_binary(url):
    async with curio_http.ClientSession() as session:
        response = await session.get(url)
        response.raise_for_status()
        return await response.binary()
    #TODO: Check if I need to swallow error here, like the original code

async def download_tar_ball_of(name, version, download_dir):
    file_name = build_filename(name, version)
    url = build_url(name, version)
    print('Started download of: {}'.format(file_name))
    file_data = await get_binary(url)
    print('Finished download of: {}'.format(file_name))
    parent_dir = os.path.join(download_dir, name)
    os.makedirs(parent_dir, exist_ok=True)
    async with curio.io.FileStream(open(os.path.join(parent_dir, file_name), 'wb')) as tar_file:
        await tar_file.write(file_data)
