from sources.oxitems import OxItems
from utils.nesting_exception import log_exception
import logging
from oxtalks.oxtalks_api import OxTalksAPI
from models import is_worthy_talk
from sources.oxford_university_whatson import WhatsOn
import itertools

logging.basicConfig()
logger = logging.getLogger("OUEventsAggregationSystem")

def pull_events():

    source = WhatsOn()
    #source = OxItems()
    talks_api = OxTalksAPI("talks-ox-dev.nsms.ox.ac.uk", "richard.hills@gmail.com", "richard")

    talks, lists = talks_api.load_talks()

    new_talks = source(lists)

    new_talks = itertools.ifilter(is_worthy_talk, new_talks)
    #new_talks = itertools.islice(new_talks, 0, 4)

    talks_api.upload(new_talks)

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
