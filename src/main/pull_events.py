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

logging.basicConfig()
logger = logging.getLogger("OUEventsAggregationSystem")

"""getOII(), getStAntonys(), getPhysics(), getPolitics(), getRobotics(),
                getMaths(), getEconomics(), getTheology(), getWIMM(), getDPAG2011(), getOxfordWhatsOn(),
                getOxUniversityScientificSociety(), getEngineeringSociety(), getMaterialsSociety(),
                getOUInformationSecurityPrivacyProgramme())"""

# ICal OII, StAntonys, Politics, robotics, theology, WIMM, DPAG, Scientific Society, Engineering Society, Materials Society, Information Security

def _load_talks_from_source(source, list_manager):
    try:
        return source(list_manager)
    except:
        log_exception(logger, "Failed to load from source %s" % source)

def pull_events():

    #source = EventRSSSource("http://www.oii.ox.ac.uk/events/feed/")
    #source = WhatsOn()
    #source = OxItems()

    talks_api = OxTalksAPI("talks-ox-dev.nsms.ox.ac.uk", "richard.hills@gmail.com", "richard")
    talks, lists = talks_api.load_talks()

    with ThreadPoolExecutor(max_workers=3) as executor:
        # Pull from sources on multiple threads at once
        sources = create_sources()
        new_talks = itertools.chain.from_iterable(executor.map(lambda source: _load_talks_from_source(source, lists), sources))

        for talk in new_talks:
            print talk
        #new_talks = itertools.ifilter(is_worthy_talk, new_talks)

        #for talk in new_talks:
        #    print talk

    #new_talks = itertools.islice(new_talks, 0, 4)

    #talks_api.upload(new_talks)

    #l = TalksList("Testing List Creation", managed_lists_type)
    #talks_api._post_create_managed_list(l)

    #old_talks, old_lists = talks_api.load_talks()
    #talks_api.upload(source())

    print "1"

    #source = OxItems()

    #for event in source():
    #    print event

try:
    if __name__ == "__main__":
        pull_events()
except:
    log_exception(logger, "Unrecoverable Error")
