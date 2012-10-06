from collections import defaultdict
import itertools
from utils import safe_len
import datetime
import pytz
from threading import RLock

class Event(object):
    __slots__ = ["name", "description", "start", "end", "location", "speaker", "lists", "master_list", "id"]

    def __init__(self, name=None, description=None, start=None, end=None, location=None,
                 speaker=None, lists=None, master_list=None, id=None):

        if getattr(start, "tzinfo", None) is None:
            raise ValueError()
        if getattr(end, "tzinfo", None) is None:
            raise ValueError()

        self.name = name
        self.description = description
        self.start = start
        self.end = end
        self.location = location
        self.speaker = speaker
        if master_list not in lists:
            raise ValueError("Master list must be in lists")
        self.lists = lists
        self.master_list = master_list
        self.id = id

    def clone_with_modifications(self, **kwargs):
        original = dict((k, getattr(self, k)) for k in self.__slots__)
        original.update(kwargs)
        return Event(**original)

    def __repr__(self):
        return "Event<%s>" % (self.name)

def is_worthy_talk(talk):
    return safe_len(talk.name) > 0 and talk.start is not None and talk.start > datetime.datetime.now(pytz.utc)

def organise_talks_by_master_list(talks):
    results = defaultdict(list)
    for talk in talks:
        results[talk.master_list].append(talk)
    return results

def merge_talks_by_key(talks, old_talks, key_gen, combine_talks):
    similar_talks = defaultdict(list)
    for talk in talks:
        similar_talks[key_gen(talk)].append(talk)

    old_talks_by_id = dict((talk.id, talk) for talk in old_talks)
    old_talks_by_key = dict((key_gen(talk), talk) for talk in old_talks)

    reduced_talks = dict()
    for key, talks in similar_talks.iteritems():
        old_talk = old_talks_by_key.get(key, None)
        reduced_talks[key] = combine_talks(old_talk, talks)

    for reduced_talk in reduced_talks.values():
        if reduced_talk.id is not None:
            del old_talks_by_id[reduced_talk.id]

    return reduced_talks, old_talks_by_id.values()

def standard_talk_key(talk):
    return (unicode(talk.name), talk.start)

def first_non_none(items, key):
    for item in items:
        if key(item) is not None:
            return item

def _safe_len(obj):
    if obj is None:
        return 0
    else:
        return len(obj)

def standard_combine_talks(old_talk, new_talks):
    lists = set(itertools.chain.from_iterable(map(lambda talk: talk.lists + [talk.master_list], new_talks)))
    if old_talk is not None:
        #lists.update(old_talk.lists)
        master_list = old_talk.master_list
        id = old_talk.id
    else:
        master_list = new_talks[0].master_list
        id = None
    lists.add(master_list)
    lists = list(lists)

    longest_description = max(new_talks, key=lambda talk: _safe_len(talk.description)).description
    end = max(new_talks, key=lambda talk: talk.end).end
    location = getattr(first_non_none(new_talks, key=lambda talk: talk.location), "location", None)
    speaker = getattr(first_non_none(new_talks, key=lambda talk: talk.speaker), "speaker", None)

    return new_talks[0].clone_with_modifications(lists=lists,
                                                description=longest_description,
                                                end=end,
                                                location=location,
                                                speaker=speaker,
                                                id=id)

#def organise_talks(talks):
#    talks_in_lists = organise_talks_by_master_list(talks)
#    structured_talks_in_lists = dict()
#    for talk_list, talks in talks_in_lists.iteritems():
#        unique_talks = organise_talks_by_key(talks, standard_talk_key, standard_combine_talks)
#        structured_talks_in_lists[talk_list] = unique_talks
#    return structured_talks_in_lists

class TalksList(object):
    __slots__ = ['name', 'list_type', 'id']
    def __init__(self, name, list_type, id):
        if name is None:
            raise ValueError("Name can't be none")
        self.name = name
        self.list_type = list_type
        self.id = id

    def __repr__(self):
        return "List<%s, %s>" % (self.id, self.name)

    @property
    def is_managed_list(self):
        return self.list_type == managed_lists_type

managed_lists_type = "managed"

class TalksListManager(object):
    def __init__(self):
        self.lists_by_id = dict()
        self.managed_lists_by_name = dict()
        self.lock = RLock()

    def get_list_by_id(self, id):
        with self.lock:
            return self.lists_by_id.get(id, None)

    def get_managed_list_by_name(self, name):
        with self.lock:
            return self.managed_lists_by_name.get(name, None)

    def get_or_create_managed_list_by_name(self, name):
        with self.lock:
            list = self.managed_lists_by_name.get(name, None)
            if list is None:
                list = TalksList(name, managed_lists_type, None)
                self.managed_lists_by_name[name] = list
            return list

    def get_or_create_list_by_id(self, id, name, list_type):
        with self.lock:
            list = self.lists_by_id.get(id, None)
            if list is None:
                if name is None or type is None:
                    raise ValueError("Couldn't instantiate new list")
                list = TalksList(name, list_type, id)
                self.lists_by_id[id] = list
                if list.is_managed_list:
                    self.managed_lists_by_name[name] = list
            return list
