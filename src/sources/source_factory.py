from yaml import load, dump
from bunch import bunchify
import sources as sources_package
from sources.ical_event_source import ICalEventSource

def _find_class(class_name):
    type_search = sources_package
    for component in class_name.split("."):
        type_search = getattr(type_search, component)
    return type_search

_types = dict(ical=ICalEventSource)

def create_sources():
    sources_dict = bunchify(load(file("../event_sources.yml")))

    sources = []

    for source_dict in sources_dict.sources:
        type_of_source = source_dict.pop("type", None)
        if type_of_source is not None:
            class_of_source = _types[type_of_source]
        else:
            class_name = source_dict.pop("class", None)
            class_of_source = _find_class(class_name)

        sources.append(class_of_source(**source_dict))

    return sources
