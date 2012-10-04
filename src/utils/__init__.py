
def safe_len(obj, default=0):
    if obj is None:
        return default
    else:
        return len(obj)
