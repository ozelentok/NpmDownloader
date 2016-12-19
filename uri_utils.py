def is_uri(version):
    if type(version) is not str:
        return False
    if version.startswith('http://'):
        return True
    if version.startswith('https://'):
        return True
    if version.startswith('git://'):
        return True
    return False
