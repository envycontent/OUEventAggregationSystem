from main.main_logging import get_logger
from sources.ical_event_source import load_ical
from utils.nesting_exception import log_exception, log_exception_via
from utils.parsing import de_list
from utils.url_load import load_soup, url_opener
import logging

logger = get_logger(__name__)

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

    name = "OxItems"
    description = "Trawls events from http://rss.oucs.ox.ac.uk/oxitems/generateicalendar1.php"

    @classmethod
    def create(cls):
        return OxItems()

    def __call__(self, list_manager):
        oxitems_list = list_manager.get_or_create_managed_list_by_name("OxItems")
        soup = load_soup(url_opener(OxItems.url))
        all_events = []
        for oxitems_feed_option in soup.xpath("//option"):
            try:
                oxitems_feed_id, = oxitems_feed_option.xpath("@value")
                if oxitems_feed_id != "_UNSET_":
                    oxitems_feed_longname, = oxitems_feed_option.xpath("text()")
                    oxitems_feed_longname = oxitems_feed_longname[len(oxitems_feed_id) + 2:]
                    master_list = list_manager.get_or_create_managed_list_by_name(oxitems_feed_longname)
                    ical_url = OxItems.feed_url % oxitems_feed_id
                    new_events = list(load_ical(url_opener(ical_url), url_for_logging=ical_url,
                                                lists=[oxitems_list, master_list],
                                                master_list=list_manager.get_or_create_managed_list_by_name(oxitems_feed_longname)))
                    logger.debug("OxItems: loaded %i talks from %s" % (len(new_events), ical_url))
                    all_events.extend(new_events)
            except Exception:
                log_exception_via(logger.warning, "OxItems failed on %s (%s)" % (oxitems_feed_id, ical_url))
        return all_events
