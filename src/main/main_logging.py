import logging
import logging.config
from logging import handlers
from settings import SettingsError

_base_logger_name = "OUEAS"

def get_logger(class_name):
    logger_name = "%s.%s" % (_base_logger_name, class_name)
    return logging.getLogger(logger_name)

aggregator_summary_logger = get_logger("AggregationSummary")

def load_main_logging(filename):
    try:
        logging.config.fileConfig(filename)
    except Exception:
        raise SettingsError("Failed to load logging configuration from %s" % filename)
