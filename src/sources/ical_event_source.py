from icalendar import Calendar
import models
from utils.parsing import local_tz
import datetime
from utils.nesting_exception import log_exception
import logging
from utils.url_load import url_opener

logger = logging.getLogger(__name__)

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
            try:
                name = component.get("summary")
                start = component.get("dtstart").dt
                end = component.get("dtend").dt
                location = component.get("location")
                description = component.get("description")
                if not isinstance(start, datetime.datetime) or not isinstance(end, datetime.datetime):
                    continue

                if start.tzinfo is None:
                    start = local_tz.localize(start, is_dst=True)
                if end.tzinfo is None:
                    end = local_tz.localize(end, is_dst=True)
                if len(name) > 0:
                    yield models.Event(name=name, start=start, end=end,
                                       location=location, description=description,
                                       master_list=master_list, lists=lists)
            except Exception:
                log_exception(logger, "Failed to create event")

class ICalEventSource(object):
    """ An event source which reads ical data from a specified context manager """
    def __init__(self, url=None, name=None):
        self.opener = url_opener(url)
        self.master_list_name = name

    def __call__(self, list_manager):
        master_list = list_manager.get_or_create_managed_list_by_name(self.master_list_name)
        return load_ical(self.opener, master_list=master_list)

