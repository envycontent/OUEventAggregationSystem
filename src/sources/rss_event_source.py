import feedparser
from bunch import bunchify
from dateutil import parser
from lxml import etree
from models import Event

def _safe(func, default):
    try:
        return func()
    except Exception:
        return default

class EventRSSSource(object):
    """ http://web.resource.org/rss/1.0/modules/event/
    
    Currently contains code specific to the OII
    """
    def __init__(self, url=None, name=None):
        self.url = url
        self.name = name

    @classmethod
    def create(cls, url, name):
        return EventRSSSource(url, name)

    def __call__(self, list_manager):
        feed = feedparser.parse(self.url)
        master_list = list_manager.get_or_create_managed_list_by_name(feed.feed.title_detail.value)

        for entry in feed.entries:
            location = entry.ev_location
            start_datetime = parser.parse(entry.ev_startdate)
            end_datetime = parser.parse(entry.ev_enddate)
            name = entry.title_detail.value
            summary_blob = entry.summary_detail.value

            # OII specific code
            link = entry.id
            summary_soup = etree.fromstring("<root>%s</root>" % summary_blob)
            def _get_speaker():
                speaker, = summary_soup.xpath("p[@class='location']/text()")
                return speaker[len("Speakers: "):]
            def _get_description():
                description, = summary_soup.xpath("p[@class='summary']/text()")
                return "%s\nTaken from %s" % (description, link)

            speaker = _safe(_get_speaker, None)
            description = _safe(_get_description, None)

            yield Event(name=name, start=start_datetime, end=end_datetime,
                        description=description, speaker=speaker, location=location,
                        master_list=master_list, lists=[master_list])
