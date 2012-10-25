from yaml import load
from bunch import bunchify
import sources as sources_package
from sources import ical_event_source, oxford_university_whatson, oxitems, rss_event_source
from utils import find_thing

_types = dict(ical=ical_event_source.ICalEventSource)

def load_sources(filename):
    sources_dict = bunchify(load(file(filename)))

    sources = []

    for source_dict in sources_dict.sources:
        type_of_source = source_dict.pop("type", None)
        if type_of_source is not None:
            class_of_source = _types[type_of_source]
        else:
            class_name = source_dict.pop("class", None)
            class_of_source = find_thing(class_name, sources_package)

        sources.append(class_of_source.create(**source_dict))

    return sources
