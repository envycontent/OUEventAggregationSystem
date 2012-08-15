from sources.oxitems import OxItems
from utils.nesting_exception import log_exception
import logging

logging.basicConfig()
logger = logging.getLogger("OUEventsAggregationSystem")

def pull_events():
    source = OxItems()

    for event in source():
        print event

try:
    if __name__ == "__main__":
        pull_events()
except:
    log_exception(logger, "Unrecoverable Error")
