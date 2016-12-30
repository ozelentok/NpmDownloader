import semver

def is_uri(version):
    if version is None:
        return False
    if not isinstance(version, (str, )):
        return False
    if version.startswith('http://'):
        return True
    if version.startswith('https://'):
        return True
    if version.startswith('git://'):
        return True
    return False

def parse_uri(uri):
    if uri.startswith('git:'):
        return uri.replace('git:', 'http:').replace('.git', '/archive/master.zip')
    return uri

def find_lastest_satisfying_version(versions, ver):
    if is_uri(ver):
        return parse_uri(ver)
    return semver.max_satisfying(versions, parse_version(ver), loose=True)

def parse_version(ver):
    return '>0.0.0' if ver == 'latest' else ver
