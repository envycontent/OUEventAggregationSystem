from sources.ical_event_source import load_ical
from sources.events_source_exception import EventSourceException
from utils.url_load import load_soup, url_opener
from utils.nesting_exception import log_exception
import logging

logger = logging.getLogger(__name__)

class OxItems(object):
    """ Loads all events in the OxItems system 
    http://www.oucs.ox.ac.uk/oxitems/
    
    We load the main page, and use an xpath to extract the names of all oxitems
    feed names from the html. We then construct an ical feed url from the 
    feednames, before loading and reading the ical files.
    
    If any particular feed fails, we log it and carry on.
    """

    url = "http://rss.oucs.ox.ac.uk/oxitems/generateicalendar1.php"
    feed_url = "http://rss.oucs.ox.ac.uk/oxitems/events.ics?channel_name=%s"

    def __call__(self):
        soup = load_soup(url_opener(OxItems.url))
        for oxitems_feed in soup.xpath("//option/@value"):
            try:
                if oxitems_feed != "_UNSET_":
                    ical_url = OxItems.feed_url % oxitems_feed
                    for event in load_ical(url_opener(ical_url)):
                        yield event
            except:
                log_exception(logger, "Oxitems failed on %s (%s)" % (oxitems_feed, ical_url))
