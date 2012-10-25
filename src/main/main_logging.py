import logging
import logging.config
from logging import handlers
from yaml import load
from settings import SettingsError

_base_logger_name = "OUEAS"

def get_logger(class_name):
    logger_name = "%s.%s" % (_base_logger_name, class_name)
    print logger_name
    return logging.getLogger(logger_name)

aggregator_summary_logger = get_logger("AggregationSummary")

def load_pull_events_logging(filename):
    try:
        logging.config.dictConfig(load(file(filename)))
    except Exception:
        raise SettingsError("Failed to load logging configuration from %s" % filename)
