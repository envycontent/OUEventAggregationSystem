from __future__ import print_function
import sys
import traceback
from StringIO import StringIO

"""
    A Python exception for "nesting" exceptions, as in Java and C#. This will
    be unecessary in Python 3, thanks to pep-3134.
    
    http://www.python.org/dev/peps/pep-3134/
    
    A couple of restrictions: Firstly new instances of this exception must be
    created within the catch block of the exception to be nested. Secondly,
    use the following for logging your exceptions, which handles nesting
    exceptions and normal exceptions:
    
    try:
        pass
    except Exception:
        log_exception(logger)
"""

class NestingException(Exception):

    def __init__(self, *args):
        super(NestingException, self).__init__(*args)
        self.nested_type, self.nested_exception, self.nested_traceback = sys.exc_info()

    def print_exc(self, output_file=sys.stdout):
        """ Method for printing this exception to a file type object.
        Must be called from within the except block to grab the outer most
        stack trace. """
        our_type, our_exception, our_traceback = sys.exc_info()
        traceback.print_exception(our_type, our_exception, our_traceback, file=output_file)
        if self.nested_type != None:
            print("Caused by:", file=output_file)

        if self.nested_exception != None:
            self._print_exc(output_file)

    def log_exc(self, logger_method):
        """ Method for printing this exception to a logger. 
        Must be called from within the except block to grab the outer most
        stack trace. """
        message = StringIO()
        self.print_exc(message)
        logger_method(message.getvalue())

    def _print_exc(self, output_file):
        """ Recursive method for printing our nested exception and any further children """
        traceback.print_exception(self.nested_type, self.nested_exception, self.nested_traceback, file=output_file)
        if isinstance(self.nested_exception, NestingException):
            print("Caused by:", file=output_file)
            self.nested_exception._print_exc(output_file)

def log_exception_via(logger_method, msg):
    """ Generic method for logging any exceptions, but also handles NestingExceptions """
    nested_type, nested_exception, nested_traceback = sys.exc_info()
    if isinstance(nested_exception, NestingException):
        # Log the message, but handle logging the exception ourselves
        logger_method(msg)
        nested_exception.log_exc(logger_method)
    else:
        # Use standard logging for the exception
        logger_method(msg, exc_info=True)

def log_exception(logger, msg):
    """ Generic method for logging any exceptions, but also handles NestingExceptions """
    log_exception_via(logger.error, msg)
