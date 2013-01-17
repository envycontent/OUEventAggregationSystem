
def safe_len(obj, default=0):
    if obj is None:
        return default
    else:
        return len(obj)

__no_default = object()

def find_thing(thing_name, start, default=__no_default):
    type_search = start
    for component in thing_name.split("."):
        type_search = getattr(type_search, component, None)
        if type_search == None:
            if default == __no_default:
                raise AttributeError("Failed to find thing %s" % thing_name)
            else:
                return default
    return type_search
