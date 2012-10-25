
def safe_len(obj, default=0):
    if obj is None:
        return default
    else:
        return len(obj)

def find_thing(thing_name, start):
    type_search = start
    for component in thing_name.split("."):
        type_search = getattr(type_search, component)
    return type_search
