from utils.url_load import load_soup, url_opener, absolute_url
from sources.ical_event_source import load_ical

_main_page_url = "http://www.dailyinfo.co.uk/events/lectures"

class DailyInfo(object):
    name = "Daily Info"
    description = "The Daily Info website events: %s" % _main_page_url
    
    @classmethod
    def create(cls):
        return DailyInfo()

    def __call__(self, list_manager):
        soup = load_soup(url_opener(_main_page_url))
        master_list = list_manager.get_or_create_managed_list_by_name("Daily Info")
        
        for ical_link in soup.xpath("//@href[contains(., 'generate_ics')]"):
            ical_uri = absolute_url(_main_page_url, ical_link)
            for event in load_ical(url_opener(ical_uri), 
                                   master_list=master_list, 
                                   url_for_logging=_main_page_url):
                yield event
        
