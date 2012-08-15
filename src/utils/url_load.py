from contextlib import contextmanager
import urllib2
from lxml.html import soupparser
import re

""" Utility methods that are useful to loading urls """

def do_nothing_context_manager(method, *args, **kwargs):
    def func():
        yield method(*args, **kwargs)
    return contextmanager(func)

def url_opener(url):
    """ Given a url, returns a context manager object that will load it. You 
    could do:
    
    s = ICalEventSource(url_opener("http://www.medsci.ox.ac.uk/research/seminars/seminars-in-the-msd/ics_view")) """
    return do_nothing_context_manager(urllib2.urlopen, url)

def load_soup(open):
    """ From a context manager, loads a url and interprets it into a soup object,
    that represents a DOM """
    with open() as file:
        return soupparser.fromstring(file.read())

def split_url(url):
    """ Breaks up a url into protocol, host and path """
    protocol_host_path_matches = re.findall("^(?:(https?)://)?(.*?)(/.*)$", url)
    return protocol_host_path_matches[0]

def _use_non_empty(first, second):
    return first if first != None and first != "" else second

def absolute_url(page_url, link):
    """ Converts a relative url into an absolute url. link is the relative
    url, while page_url is that of the page where the link was found """
    protocol, host, path = split_url(page_url)
    if not path.endswith("/"):
        path, sep, file = path.rpartition("/")
        path = path + "/"
    link_protocol, link_host, link_path = split_url(link)

    protocol_to_use = _use_non_empty(link_protocol, protocol)
    host_to_use = _use_non_empty(link_host, host)
    if link_path.startswith("/"):
        path_to_use = link_path
    else:
        path_to_use = path + link_path

    return "%s://%s%s" % (protocol_to_use, host_to_use, path_to_use)
