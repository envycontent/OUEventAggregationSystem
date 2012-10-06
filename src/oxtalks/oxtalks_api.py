from lxml import etree
from lxml.html import soupparser
from models import Event, TalksListManager, managed_lists_type, \
    standard_combine_talks, standard_talk_key, merge_talks_by_key
from sources.exceptions import OxTalksAPIException
from sources.ical_event_source import load_ical
from urllib2 import HTTPError
from utils.url_load import url_opener, load_soup, url_open
from xml.etree.ElementTree import Element, SubElement, tostring
import base64
import dateutil.parser
import requests
import urllib
import urllib2
import urlparse
import StringIO
from xml.sax.saxutils import escape, unescape

def safe_unpack(l):
    if len(l) == 0:
        return None
    elif len(l) > 1:
        raise ValueError
    else:
        return l[0]

def safe_str(o):
    return str(o) if o is not None else ""

def safe(func, error=Exception, default=""):
    try:
        return func()
    except:
        return default

def _create_time(time):
    return "%s:%s" % (time.hour, time.minute)

def _create_date(date):
    return "%s/%s/%s" % (date.year, date.month, date.day)

def _format_location(location):
    return location or ""

class OxTalksAPI(object):

    def __init__(self, host, username, password):
        self.host = host
        self.old_talks = None
        self.username = username
        self.auth = (username, password)

    def upload(self, talks):
        if self.old_talks is None:
            raise OxTalksAPIException("Talks not loaded")

        new_talks, old_redundant_talks = merge_talks_by_key(talks, self.old_talks, standard_talk_key, standard_combine_talks)

        for new_talk in new_talks.values():
            for list in new_talk.lists:
                if list.is_managed_list and list.id is None:
                    list.id = self._post_create_managed_list(list)
            self._post_update_talk(new_talk)

        for talk in old_redundant_talks:
            self._delete_talk(talk)

    def _post_update_talk(self, talk):
        url = 'http://%s/talk/update/' % self.host
        if talk.id is not None:
            url = url + str(talk.id)

        print "UPDATE %s" % url

        data = [("talk[title]", talk.name),
                ("talk[abstract]", talk.description),
                ("talk[name_of_speaker]", talk.speaker),
                ("talk[venue_name]", talk.location),
                ("talk[series_id_string]", talk.master_list.id),
                ("talk[start_time_string]", _create_time(talk.start.time())),
                ("talk[end_time_string]", _create_time(talk.end.time())),
                ("talk[date_string]", _create_date(talk.start.date())),
                ("talk[organiser_email]", self.username)]

        for l in talk.lists:
            data.append(("talk[list_id_strings][]", str(l.id)))

        response = requests.post(url, data, auth=self.auth)
        if response.status_code != 200:
            raise OxTalksAPIException("Failed to create talk %s\nPost was %s" % (talk, data), response.content)

    def _delete_talk(self, talk):
        url = 'http://%s/talk/delete/%s' % (self.host, talk.id)

        print "DELETE %s" % url

        response = requests.post(url, auth=self.auth)
        if response.status_code != 200:
            raise OxTalksAPIException("Failed to delete talk %s" % talk, response.content)

    def _post_create_managed_list(self, managed_list):
        if not managed_list.is_managed_list:
            raise OxTalksAPIException("Can only create managed lists on remote Oxford Talks")
        url = 'http://%s/list/api_create' % self.host
        print "POST %s" % url
        data = {"list[name]":managed_list.name,
                                 "list[list_type]":managed_list.list_type}
        response = requests.post(url, data, auth=self.auth)
        if response.status_code != 200:
            raise OxTalksAPIException("Failed to create managed list %s" % managed_list.name, response.content)
        else:
            list_soup = soupparser.fromstring(response.content)
            return int(list_soup.xpath("list/id/text()")[0])

    def load_talks(self):
        talks, list_manager = self._load_talks()
        self.old_talks = talks
        return talks, list_manager

    def _load_talks(self):
        #talks_url = "http://%s/show/xml/4032" % self.host
        #with open("/home/richard/oxford-talks/all") as f:
        asd = None
        with url_open("http://%s/show/xml/all_future" % self.host) as f:
            asd = f.read()
        with url_open("http://%s/show/xml/all_future" % self.host) as f:
            root = etree.parse(f)
            lists_manager = TalksListManager()
            result = []
            for talk in root.xpath("/list/talk"):
                result.append(self._convert_xml_to_talk(talk, lists_manager))
            return result, lists_manager

    def _convert_xml_to_talk(self, talk_root, list_manager):
        name = safe(lambda: unicode(unescape(talk_root.xpath("title/text()")[0])))
        id, = talk_root.xpath("id/text()")
        id = int(id)
        description = safe(lambda: unicode(unescape(talk_root.xpath("abstract/text()")[0])))
        speaker = safe(lambda: unicode(unescape(talk_root.xpath("speaker/text()")[0])))
        location = safe(lambda: unicode(unescape(talk_root.xpath("venue/text()")[0])))
        start, = talk_root.xpath("start_time/text()")
        start = dateutil.parser.parse(start)
        end, = talk_root.xpath("end_time/text()")
        end = dateutil.parser.parse(end)

        lists = []
        for list in talk_root.xpath("list"):
            list_id, = list.xpath("id/text()")
            list_id = int(list_id)
            list_name, = list.xpath("name/text()")
            list_name = safe_str(list_name)
            list_type = list.xpath("list_type/text()")
            if len(list_type) > 0:
                list_type = safe_str(list_type[0])
            else:
                list_type = ""
            lists.append(list_manager.get_or_create_list_by_id(list_id, list_name, list_type))

        master_list_id, = talk_root.xpath("series/text()")
        master_list_id = int(master_list_id)
        master_list = list_manager.get_list_by_id(master_list_id)
        if master_list is None:
            raise OxTalksAPIException("Master List isn't known about yet")

        return Event(name, description, start, end, location, speaker, lists, master_list, id=id)


        #events = load_ical(url_opener(talks_url))
