NPM_REGISTRY_URL = 'http://registry.npmjs.org'

def build_all_versions_url(name):
    return '{}/{}'.format(NPM_REGISTRY_URL, name)

def build_version_url(name, version):
    return '{}/{}/{}'.format(NPM_REGISTRY_URL, name, version)

def build_tarball_url(name, version):
    return '{}/{}/-/{}'.format(NPM_REGISTRY_URL, name.replace('%2f', '/'), build_filename(name, version))

def build_filename(name, version):
    return '{}-{}.tgz'.format(unscope_name(name), version)

def normalize_package(name):
    if is_scoped(name):
        return name.replace('/', '%2f')
    return name

def is_scoped(name):
    return name.startswith('@')

def unscope_name(scoped_name):
    if is_scoped(scoped_name):
        return scoped_name.split('%2f')[1]
    return scoped_name
