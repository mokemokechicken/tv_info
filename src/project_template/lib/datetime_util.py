import re
from datetime import datetime, timedelta

import dateparser
import pytz
from dateutil import parser as dateutil_parser

JST = pytz.timezone("Asia/Tokyo")
UTC = pytz.utc


def to_yyyymmdd(date_str, support_relative_expression=True):
    day = None
    if support_relative_expression:
        try:
            days_after = int(date_str)
            if days_after < 19700101:
                day = datetime.now() + timedelta(days_after)
        except (ValueError, TypeError):
            pass
    if not day:
        day = parse_date_str(date_str)
    return day.strftime('%Y%m%d')


def to_yyyy_mm_dd(date_str):
    day = parse_date_str(date_str)
    return day.strftime('%Y-%m-%d')


def to_unixtime(date_str):
    if isinstance(date_str, int):
        return date_str
    else:
        day = parse_date_str(date_str)
        return int(day.timestamp())


def parse_date_str(s):
    """

    :param str s:
    :rtype datetime
    """
    if isinstance(s, datetime):
        return s
    try:
        re.sub('([0-9]{4})([0-9]{2})([0-9]{2})', r'\1-\2-\3', str(s))
        return dateutil_parser.parse(s)
    except (ValueError, TypeError):
        return dateparser.parse(str(s))


def from_unixtime_to_datetime(unixtime, tz=UTC):
    return datetime.fromtimestamp(unixtime, tz=tz)

