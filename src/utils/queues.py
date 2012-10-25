from utils.nesting_exception import log_exception
from main.main_logging import get_logger

_queue_finished = object()
logger = get_logger(__name__)

def close_queue(queue):
    queue.put(_queue_finished)

def queue_yielder(queue):
    """ While valid objects are coming out of the queue, yield them """
    while True:
        item = queue.get()
        if item is _queue_finished:
            break
        yield item
