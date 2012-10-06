from sources.ical_event_source import load_ical
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

    def __call__(self, list_manager):
        oxitems_list = list_manager.get_or_create_managed_list_by_name("OxItems")
        soup = load_soup(url_opener(OxItems.url))
        for oxitems_feed_option in soup.xpath("//option"):
            try:
                oxitems_feed_id, = oxitems_feed_option.xpath("@value")
                if oxitems_feed_id != "_UNSET_":
                    oxitems_feed_longname, = oxitems_feed_option.xpath("text()")
                    oxitems_feed_longname = oxitems_feed_longname[len(oxitems_feed_id) + 2:]
                    master_list = list_manager.get_or_create_managed_list_by_name(oxitems_feed_longname)
                    ical_url = OxItems.feed_url % oxitems_feed_id
                    for event in load_ical(url_opener(ical_url),
                                           lists=[oxitems_list, master_list],
                                           master_list=list_manager.get_or_create_managed_list_by_name(oxitems_feed_longname)):
                        yield event
            except Exception:
                log_exception(logger, "Oxitems failed on %s (%s)" % (oxitems_feed_id, ical_url))
