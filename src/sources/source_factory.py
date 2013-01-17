from yaml import load
from bunch import bunchify
import sources as sources_package
from sources import ical_event_source, oxford_university_whatson, oxitems, rss_event_source
from utils import find_thing
from utils.nesting_exception import NestingException

_types = dict(ical=ical_event_source.ICalEventSource)

class SourceConfigException(NestingException):
    pass

def load_sources(filename):
    sources_dict = bunchify(load(file(filename)))

    sources = []

    for source_dict in sources_dict.sources:
        type_of_source = source_dict.pop("type", None)
        class_name = source_dict.pop("class", None)
        if type_of_source is not None:
            class_of_source = _types.get(type_of_source, None)
            if class_of_source == None:
                raise SourceConfigException("Could not find type %s. Available types are %s" % (type_of_source, _types.keys()))
        elif class_name is not None:
            class_of_source = find_thing(class_name, sources_package, None)
            if class_of_source == None:
                raise SourceConfigException("Could not find class %s" % (class_name))
        else:
            raise SourceConfigException("The following source config did not specify either a class or type: %s" % source_dict)

        try:
            sources.append(class_of_source.create(**source_dict))
        except Exception:
            raise SourceConfigException("Failed to create source %s" % type_of_source if type_of_source is not None else class_name)

    return sources
