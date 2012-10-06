import feedparser
from bunch import bunchify
from dateutil import parser
from lxml import etree
from models import Event

class EventRSSSource(object):
    """ http://web.resource.org/rss/1.0/modules/event/
    
    Currently contains code specific to the OII
    """
    def __init__(self, url=None):
        self.loader = url

    def __call__(self, list_manager):
        feed = feedparser.parse(self.loader)
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
            speaker, = summary_soup.xpath("p[@class='location']/text()")
            speaker = speaker[len("Speakers: "):]
            description, = summary_soup.xpath("p[@class='summary']/text()")

            description = "%s\nTaken from %s" % (description, link)

            yield Event(name=name, start=start_datetime, end=end_datetime,
                        description=description, speaker=speaker, location=location,
                        master_list=master_list, lists=[master_list])
