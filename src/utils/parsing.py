import re
import pytz

local_tz = pytz.timezone('Europe/London')

def de_list(arg):
    """ Useful for cases where a function returns a single object or a list, depending on what was found. Silly python """
    if isinstance(arg, list):
        for obj in arg:
            yield obj
    else:
        if arg != None:
            yield arg

def convert_to_utc(*dts):
    def utc_normalize(dt):
        return pytz.utc.normalize(dt.astimezone(pytz.utc))
    return [utc_normalize(dt) for dt in dts]

def render_html_text(node):
    return _handle_whitespace_in_html_while_preserving_new_lines(_render_html_text(node)).strip()

def _handle_whitespace_html(text):
    text = re.sub("\s+", " ", text)
    return re.sub("\s", " ", text)

def _handle_whitespace_in_html_while_preserving_new_lines(text):
    return "\n".join(_handle_whitespace_html(chunk).strip() for chunk in text.rsplit("\n"))

def _render_html_text(node):
    if isinstance(node, basestring):
        return _handle_whitespace_html(node)

    result = ""

    for child in node.xpath("* | text()"):
        if isinstance(child, basestring):
            result += _handle_whitespace_html(child)
        elif child.tag == "p":
            result += _render_html_text(child) + "\n"
        elif child.tag == "br":
            result += "\n"
        else:
            result += _render_html_text(child)
    return result
