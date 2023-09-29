import re
import time
from slugify import slugify
from datetime import timedelta, timezone


def get_valid_filename(name):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    return s


def utc_to_local(utc_dt):
    tz = timezone(timedelta(seconds=time.localtime().tm_gmtoff))
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=tz)
