from utils.nesting_exception import log_exception
from oxtalks.oxtalks_api import OxTalksAPI, DeleteOutstanding, AddEvent
from models import is_worthy_talk
import itertools
from sources.source_factory import load_sources
from concurrent.futures import ThreadPoolExecutor
from main.main_logging import get_logger, aggregator_summary_logger, load_pull_events_logging
from Queue import Queue
from utils.queues import close_queue, queue_yielder
import time
from sources.oxford_university_whatson import WhatsOn
import threading
from sources.ical_event_source import ICalEventSource
from optparse import OptionParser
import logging
from settings import load_settings

# Until we load logging information from our configuration file
logging.basicConfig()

logger = get_logger("pull_events")

def _load_talks_from_source(source, list_manager, instructions_queue):
    number_of_events_loaded = 0
    started = time.time()
    succeeded = True
    try:
        logger.info("Loading events from %s" % source)
        for event in source(list_manager):
            instructions_queue.put(AddEvent(event))
            number_of_events_loaded = number_of_events_loaded + 1
        logger.info("Finished loading events from %s" % source)
        return True
    except Exception:
        log_exception(logger, "Failed to load from source %s" % source)
        succeeded = False
        return False
    finally:
        aggregator_summary_logger.info("Source %s finished %s. It took %i to return %i events" % (source, "successfully" if succeeded else "unsuccessfully", time.time() - started, number_of_events_loaded))

def _upload_talks(api, instructions):
    try:
        api.upload(instructions)
    except:
        log_exception(logger, "Failed to upload events to OxTalks")

def pull_events(settings_filename):
    settings = load_settings(settings_filename)
    load_pull_events_logging(settings.logging_config_filename)

    talks_api = OxTalksAPI(settings.oxtalks_hostname, settings.oxtalks_username,
                           settings.oxtalks_password)
    talks, list_manager = talks_api.load_talks()
    instructions_queue = Queue()

    source_futures = []
    upload_future = None

    # We load events on a series of worker threads, while another thread
    # uploads the events onto OxTalks.

    # 'with' statement blocks on Executors until all outstanding jobs are
    # complete.
    with ThreadPoolExecutor(max_workers=1) as upload_executor:
        try:
            # Start our upload events task. It loads events from the instruction_queue
            # Set up filters for boring events
            new_instructions = itertools.ifilter(lambda instruction: not isinstance(instruction, AddEvent) or is_worthy_talk(instruction.event),
                                                 queue_yielder(instructions_queue))
            upload_future = upload_executor.submit(_upload_talks, talks_api, new_instructions)

            with ThreadPoolExecutor(max_workers=3) as source_executor:
                # Start running our various event sources
                for source in load_sources(settings.sources_filename):
                    source_futures.append(source_executor.submit(_load_talks_from_source, source, list_manager, instructions_queue))
            # All the sources will now have finished running
            all_sources_succeeded = True
            for source_future in source_futures:
                if not source_future.result():
                    all_sources_succeeded = False
            if all_sources_succeeded:
                instructions_queue.put(DeleteOutstanding())
        finally:
            # Closing the queue terminates the upload job
            close_queue(instructions_queue)

        # Force any exception from the uploader to be thrown.
        if upload_future is not None:
            upload_future.result()

try:
    if __name__ == "__main__":
        parser = OptionParser()
        parser.add_option("-s", "--settings_file", dest="settings_filename",
                          help="location of settings file", metavar="FILE")
        (options, args) = parser.parse_args()

        pull_events(settings_filename=options.settings_filename)
except:
    log_exception(logger, "Unrecoverable Error")
