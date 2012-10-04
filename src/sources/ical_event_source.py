from icalendar import Calendar, Event
from utils.nesting_exception import NestingException
import models

def load_ical(open, raw_hacks=[], master_list=None, lists=[]):
    """ Utility method to load an ical file and yield the events within it """
    with open() as stream:
        text = stream.read()
        if text == "":
            # Stupid bug in Calendar parser, doesn't accept empty files.
            return

        for raw_hack in raw_hacks:
            text = raw_hack(text)

        calendar = Calendar.from_string(text)

        for component in calendar.walk('VEVENT'):
            name = component.get("summary")
            #if from_oxford_talks:
            #    name, hacked_speaker_name = name.lsplit(" -- ", 1)
            start = component.get("dtstart").dt
            end = getattr(component.get("dtend"), "dt", None)
            #speaker = component.get("X-TALK-SPEAKER")
            if len(name) > 0 and getattr(start, "tzinfo", None) is not None:
                yield models.Event(name=name, start=start, end=end, master_list=master_list, lists=lists)

class ICalEventSource(object):
    """ An event source which reads ical data from a specified context manager """
    def __init__(self, open):
        self.open = open

    def __call__(self):
        return load_ical(self.open)
