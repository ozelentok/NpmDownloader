import semver
from uri_utils import is_uri

def get_lastest_satisfying_version(versions, ver):
    if is_uri(ver):
        return parse_uri(ver)
    return semver.max_satisfying(versions, parse_version(ver), loose=True)

def parse_uri(uri):
    if uri.startswith('git:'):
        return uri.replace('git:', 'http:').replace('.git', '/archive/master.zip')
    return uri

def parse_version(ver):
    return '>0.0.0' if ver == 'latest' else ver
