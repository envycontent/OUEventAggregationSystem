from sources.oxitems import OxItems
from utils.nesting_exception import log_exception
import logging
from oxtalks.oxtalks_api import OxTalksAPI
from models import is_worthy_talk
from sources.oxford_university_whatson import WhatsOn
import itertools
from sources.rss_event_source import EventRSSSource
from sources.source_factory import create_sources
from concurrent.futures import ThreadPoolExecutor
from main.main_logging import pull_events_basic_logging

pull_events_basic_logging()

logger = logging.getLogger("OUEventsAggregationSystem")

def _load_talks_from_source(source, list_manager):
    try:
        logger.info("Loading events from %s" % source)
        return list(source(list_manager))
    except Exception:
        log_exception(logger, "Failed to load from source %s" % source)
        return []

def pull_events():
    talks_api = OxTalksAPI("talks-ox-dev.nsms.ox.ac.uk", "richard.hills@gmail.com", "richard")
    talks, lists = talks_api.load_talks()

    with ThreadPoolExecutor(max_workers=5) as executor:
        # Pull from sources on multiple threads at once
        sources = create_sources()
        new_talks = itertools.chain.from_iterable(executor.map(lambda source: _load_talks_from_source(source, lists), sources))

        new_talks = itertools.ifilter(is_worthy_talk, new_talks)

        talks_api.upload(new_talks)

try:
    if __name__ == "__main__":
        pull_events()
except:
    log_exception(logger, "Unrecoverable Error")
