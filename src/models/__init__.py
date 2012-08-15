
class Event(object):
    __slots__ = ["name", "description", "start", "end", "location", "speaker", "list_names", "master_list_name"]

    def __init__(self, name=None, description=None, start=None, end=None, location=None, speaker=None, list_names=None, master_list_name=None):
        self.name = name
        self.description = description
        self.start = start
        self.end = end
        self.location = location
        self.speaker = speaker
        self.list_names = list_names
        self.master_list_name = master_list_name

    def clone_with_modifications(self, **kwargs):
        original = dict((k, getattr(self, k)) for k in self.__slots__)
        original.update(kwargs)
        return Event(**original)

    def __repr__(self):
        return "Event<%s>" % (self.name)
