from Queue import Queue
from concurrent.futures import ThreadPoolExecutor, Future
from main.main_logging import get_logger, aggregator_summary_logger, \
    load_main_logging
from models import is_worthy_talk, TalksListManager
from optparse import OptionParser
from oxtalks.oxtalks_api import OxTalksAPI, DeleteOutstanding, AddEvent
from settings import load_settings
from sources.ical_event_source import ICalEventSource
from sources.oxford_university_whatson import WhatsOn
from sources.source_factory import load_sources
from utils.nesting_exception import log_exception
import itertools
import logging
import threading
import time

# Until we load logging information from our configuration file
logging.basicConfig()

logger = get_logger("pull_events")

def _load_talks_from_source(source, list_manager):
    started = time.time()
    succeeded = True
    new_instructions = []
    try:
        logger.info("Loading events from %s" % source)
        for event in source(list_manager):
            new_instructions.append(AddEvent(event))
        logger.info("Finished loading events from %s" % source)
        return new_instructions, True
    except Exception:
        log_exception(logger, "Failed to load from source %s" % source)
        succeeded = False
        # Return as many events as we were able to fetch. Maybe should return [] ?
        return new_instructions, False
    finally:
        aggregator_summary_logger.info("Source %s finished %s. It took %i to return %i events" % (source, "successfully" if succeeded else "unsuccessfully", time.time() - started, len(new_instructions)))

def list_trawlers(options, settings):
    for source in load_sources(settings.sources_filename):
        print source.name
        description = getattr(source, "description", None)
        print "\t%s" % (description if description is not None else "No description available")
        print

def pull_events(options, settings):
    aggregator_summary_logger.info("Starting pull_events")
    talks_api = OxTalksAPI(settings.oxtalks_hostname, settings.oxtalks_username,
                           settings.oxtalks_password)
    
    # if not options.dry_run:
    talks, list_manager = talks_api.load_talks()
    # else:
    #    list_manager = TalksListManager()

    sources = load_sources(settings.sources_filename)
    single_trawler_to_run = getattr(options, "trawler", None)
    if single_trawler_to_run is not None:
        sources = filter(lambda source: source.name == single_trawler_to_run, sources)
        if len(sources) == 0:
            raise ValueError("Could not find trawler named %s, use --list_trawlers to see all those in the system" % single_trawler_to_run)
    all_instructions = []
    all_succeeded = True

    # Make use of threadpoolexecutor to run all sources on different threads.
    with ThreadPoolExecutor(max_workers=10) as sources_executor:
        source_results = []
        for source in sources:
            source_results.append(sources_executor.submit(_load_talks_from_source, source, list_manager))
        for new_instructions, succeeded in map(Future.result, source_results):
            all_instructions.extend(new_instructions)
            all_succeeded = all_succeeded and succeeded            

    # Remove dull events
    all_instructions = filter(lambda instruction: not isinstance(instruction, AddEvent) or is_worthy_talk(instruction.event),
                              all_instructions)
            
    if all_succeeded and single_trawler_to_run is None:
        all_instructions.append(DeleteOutstanding())

    if options.dry_run:
        for i in all_instructions:
            print i
    else:
        try:
            talks_api.upload(all_instructions)
        except:
            log_exception(logger, "Failed to upload events to OxTalks")

try:
    if __name__ == "__main__":
        parser = OptionParser()
        parser.add_option("-t", "--trawler", dest="trawler",
                         help="name of trawler to run")
        parser.add_option("-l", "--list", dest="list_trawlers",
                         action='store_true', help="list names of available trawlers")
        parser.add_option("-d", "--dry_run", dest="dry_run",
                         action='store_true', help="Dry run, don't upload to talks website")
        (options, positional_args) = parser.parse_args()
        options.settings_filename, = positional_args

        settings = load_settings(options.settings_filename)
        load_main_logging(settings.logging_config_filename)
        
        if options.list_trawlers:
            list_trawlers(options, settings)
        else:            
            pull_events(options, settings)
except:
    log_exception(logger, "Unrecoverable Error")
