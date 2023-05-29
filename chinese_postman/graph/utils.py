def all_unique(iterable):
    seen = set()
    return not any(item in seen or seen.add(item) for item in iterable)
