def is_uri(version):
    if version is None:
        return False
    if isinstance(version, (str, )):
        return False
    if version.startswith('http://'):
        return True
    if version.startswith('https://'):
        return True
    if version.startswith('git://'):
        return True
    return False
