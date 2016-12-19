def parse(name):
    if is_scoped(name):
        return name.replace('/', '%2f')
    return name

def is_scoped(name):
    return name.startswith('@')

def unscope_name(scoped_name):
    if is_scoped(scoped_name):
        return scoped_name.split('%2f')[1]
    return scoped_name
