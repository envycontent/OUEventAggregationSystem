from sources.ical_event_source import load_ical
from utils.url_load import load_soup, url_opener, absolute_url
from utils.nesting_exception import log_exception, log_exception_via
from utils.parsing import render_html_text, local_tz
import logging
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed
from main.main_logging import get_logger

url = "http://www.ox.ac.uk/applications/dynamic/index.rm?filter_type=all&count=9999&id=55"

logger = get_logger(__name__)

def munge_dst(datetime):
    """ Fixes bug in What's on Page, where ical files contain incorrect timezone info """
    if datetime is not None:
        return local_tz.localize(datetime.replace(tzinfo=None), is_dst=True)
    else:
        return None

def munge_character(text):
    """ Fixes bug where it appears their UTF-8 encoding is broken. It seems
    that UTF-8 characters like U+2019, U+201C etc are getting truncated to
    U+0019, U+001C etc. These are the old, low-ascii control codes, and seriously
    confuse the system. """
    # Substitutions taken from http://www.ibiblio.org/fred2.0/wordpress/?tag=arc
    try:
        return text.replace(u"\u0013", u"\u2013").replace(u"\u0018", u"\u2018").replace(u"\u0019", u"\u2019").replace(u"\u001c", u"\u201c").replace(u"\u001d", u"\u201d")
    except Exception:
        # A line for breakpointing on
        raise

def load_events(event_page_url, master_list, lists):
    try:
        event_page_soup = load_soup(url_opener(event_page_url))
        description_nodes = event_page_soup.xpath("//div[@class='description']")
        if len(description_nodes) > 0:
            description_node = description_nodes[0]
            description = render_html_text(description_node)
        else:
            description = ""
        description = "%s\nLoaded from \"%s\":%s" % (description, event_page_url, event_page_url)
        ical_path, = event_page_soup.xpath("//a/@href[contains(., 'add_event_to_calendar')]")
        ical_link = absolute_url(event_page_url, ical_path)
        results = []
        for event in load_ical(url_opener(ical_link), raw_hacks=[munge_character],
                           master_list=master_list, lists=lists):
            results.append(event.clone_with_modifications(description=description,
                                                          start=munge_dst(event.start),
                                                          end=munge_dst(event.end)))
        return results
    except Exception:
        log_exception_via(logger.warning, "Failed loading event from %s" % event_page_url)
        return []


class WhatsOn(object):
    name = "Oxford University What's On"
    description = "The Oxford University What's On pages: http://www.ox.ac.uk/visitors_friends/whats_on/index.html"
    
    @classmethod
    def create(cls):
        return WhatsOn()

    def __call__(self, list_manager):
        with ThreadPoolExecutor(max_workers=8) as executor:
            waiting_futures = []
            master_list = list_manager.get_or_create_managed_list_by_name("Oxford University What's On")

            soup = load_soup(url_opener(url))
            for event_element in soup.xpath("//div[@id='primary-content']//ul/li//div[@class='content']"):
                event_page_path, = event_element.xpath(".//@href[contains(., 'go.rm')]")
                series, = event_element.xpath("p[1]")
                series = list_manager.get_or_create_managed_list_by_name(render_html_text(series))
                lists = [master_list, series]
                event_page_url = absolute_url(url, event_page_path)

                waiting_futures.append(executor.submit(load_events, event_page_url, master_list, lists))

            for finished_future in as_completed(waiting_futures):
                for talk in finished_future.result():
                    yield talk
