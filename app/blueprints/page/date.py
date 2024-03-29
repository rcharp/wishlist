# import dateutil.relativedelta
# import dateutil.parser
from datetime import tzinfo, timezone, timedelta, datetime as dtime
import datetime
import time
import pytz
import tzlocal
# import app.blueprints.simple.prettydate as p
from json import dumps
from dateutil.parser import parse
import os
import platform

now = dtime.now()
yesterday = now - datetime.timedelta(days=1)
three_days_ago = now - datetime.timedelta(days=3)
one_week_ago = now - datetime.timedelta(days=7)
one_month_ago = now - datetime.timedelta(days=30)
six_weeks_ago = now - datetime.timedelta(days=45)
two_months_ago = now - datetime.timedelta(days=60)
three_months_ago = now - datetime.timedelta(days=90)
six_months_ago = now - datetime.timedelta(days=180)
twelve_months_ago = now - datetime.timedelta(days=365)
twenty_four_months_ago = now - datetime.timedelta(days=730)

"""Get timestamp################################################################
def get_timestamp(timestamp):
    timestamp = timestamp.replace("T", " ")
    timestamp = timestamp.replace("Z", "")
    time_tuple = time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(time_tuple))
    return timestamp

def convert_start_time(int_time):
    #int_time = int_time.replace("/", "-")
    int_time = str(int_time) + " 00:00:00"
    time_tuple = datetime.strptime(int_time, "%m/%d/%Y %H:%M:%S")
    return time_tuple

def convert_end_time(int_time):
    #int_time = int_time.replace("/", "-")
    int_time = str(int_time) + " 23:59:59"
    time_tuple = datetime.strptime(int_time, "%m/%d/%Y %H:%M:%S")
    return time_tuple
"""


def is_date(string, fuzzy=False):
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
    except Exception:
        return False


def is_datetime(d):
    return isinstance(d, datetime.date) or isinstance(d, dtime)


def get_creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        dt = convert_timestamp_to_datetime_utc(os.path.getctime(path_to_file))
        date = convert_datetime_to_available(dt)
        return date
    else:
        stat = os.stat(path_to_file)
        try:
            dt = convert_timestamp_to_datetime_utc(stat.st_birthtime)
            date = convert_datetime_to_available(dt)
            return date
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            dt = convert_timestamp_to_datetime_utc(stat.st_mtime)
            date = convert_datetime_to_available(dt)
            return date


# Time conversions ###################################
def get_short_date_string(timestamp):
    dt = dtime.fromtimestamp(timestamp)
    dt=dt.replace(tzinfo=None)
    return dt.strftime("%B %d")


def get_formatted_date_string(timestamp):
    dt = dtime.fromtimestamp(timestamp)
    dt=dt.replace(tzinfo=None)
    return dt.strftime("%B %d, %Y")


def get_datetime_string(timestamp):
    dt = dtime.fromtimestamp(timestamp)
    dt=dt.replace(tzinfo=None)
    return dt.strftime("%B %d, %Y %H:%M:%S")


def get_dt_string(dt):
    dt = dt.replace(tzinfo=None)
    return dt.strftime("%B %d, %Y %H:%M:%S")


def convert_string_dates(date_string):
    date_string = str(date_string)
    dt = dtime.strptime(date_string, '%Y-%m-%d')
    return '{0}/{1}/{2:02}'.format(dt.month, dt.day, dt.year)


def convert_datetime_to_available(dt):
    return '{0}/{1}/{2:02}'.format(dt.month, dt.day, dt.year)


def format_datetime(dt):
    return '{0:02}/{1:02}/{2:02}'.format(dt.month, dt.day, dt.year)


def get_string_from_datetime(dt):
    tz = tzlocal.get_localzone()
    date = tz.localize(dt)
    return date.strftime('%Y-%m-%d %H:%M:%S.%f')


def get_string_from_utc_datetime(dt, godaddy=False):
    if godaddy:
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


def get_iso_string_from_utc_datetime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S') + '+00:00'


def get_shortened_iso_string_from_utc_datetime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M')


def convert_timestamp_to_datetime_utc(timestamp):
    dt_naive_utc = dtime.utcfromtimestamp(timestamp)
    return dt_naive_utc.replace(tzinfo=pytz.utc)


def get_datetime(timestamp):
    dt = dtime.fromtimestamp(timestamp)
    dt=dt.replace(tzinfo=None)
    return dt


def get_datetime_from_string(time_string):
    time_string = str(time_string)
    time_string = time_string.replace('T', ' ').replace('Z', '').replace('+00:00', '')
    if dtime.strptime(time_string, '%m-%d-%Y'):
        dt = dtime.strptime(time_string, '%m-%d-%Y')
        return dt

    dt = dtime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
    return dt


def get_utc_datetime_from_string(time_string):
    time_string = str(time_string)
    time_string = time_string.replace('+00:00', '')
    dt = dtime.strptime(time_string, '%Y-%m-%dT%H:%M:%S')
    return dt.astimezone(pytz.UTC)


def format_datetime_string(dt):
    return dt.strftime('%B %d, %Y %H:%M:%S')
    # return get_dt_string(dt)


def get_utc_date(time_string):
    time_string = str(time_string)
    time_string = time_string.replace('+00:00', '')
    dt = dtime.strptime(time_string, '%m/%d/%Y')
    return dt.astimezone(pytz.UTC).date()


def get_utc_date_from_datetime(dt):
    date = dt.astimezone(pytz.UTC)
    return '{0}/{1}/{2:02}'.format(date.month, date.day, date.year)


def get_utc_date_today():
    return dtime.now(pytz.UTC).date


def get_utc_date_today_string():
    dt = dtime.now(pytz.UTC)
    return '{0}/{1}/{2:02}'.format(dt.month, dt.day, dt.year)


def get_today_date_string():
    dt = dtime.now(pytz.UTC)
    return '{0:02}-{1:02}-{2:02}'.format(dt.year, dt.month, dt.day)


def get_year_date_string(dt):
    if dt is not None: return dt.strftime('%Y-%m-%d')
    else: return None


def get_month_date_string(dt):
    if dt is not None: return dt.strftime('%m-%d-%Y')
    else: return ''


def convert_local_timestring_to_utc_string(time_string):
    time_string = str(time_string)
    offset = time_string[-6:]
    time_string = time_string.replace(time_string[-6:], '')
    direction = 'forward' if offset[0] == '-' else 'backward' if offset[0] == '+' else None

    if not direction:
        return

    hours = int(offset[1:3])
    minutes = int(offset[4:])

    dt = dtime.strptime(time_string, '%Y-%m-%dT%H:%M:%S')
    dt = dt + timedelta(hours=hours, minutes=minutes) if direction == 'forward' else dt - timedelta(hours=hours, minutes=minutes)
    return get_shortened_iso_string_from_utc_datetime(dt)


def get_local_timestring_offset(time_string):
    time_string = str(time_string)
    offset = time_string[-6:]
    return offset


def get_local_timestring_offset_parts(offset):
    if offset is None:
        return None, None, None

    direction = 'backward' if offset[0] == '-' else 'forward' if offset[0] == '+' else None

    if not direction:
        return None, None, None

    try:
        hours = int(offset[1:3])
        minutes = int(offset[4:])
    except Exception:
        hours = None
        minutes = None

    return direction, hours, minutes


def get_shortened_datetime_from_string(time_string):
    time_string = str(time_string)
    time_string = time_string.replace('T', ' ').replace('Z', '').replace('+00:00', '')
    dt = dtime.strptime(time_string, '%Y-%m-%d')
    return dt


def get_datetime_from_datestring(time_string):
    time_string = str(time_string)
    time_string = time_string.replace('T', ' ').replace('Z', '').replace('+00:00', '')
    dt = dtime.strptime(time_string, '%Y-%m-%d')
    return dt


# def pretty_date(timestamp):
#     dt = dtime.fromtimestamp(timestamp)
#     dt=dt.replace(tzinfo=None)
#     return p.date(dt)


def datetime_to_int(dt):
    return time.mktime(dt)


### Datetime JSON serializer###################################################
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")


def jsonify(datetime_obj):
    return dumps(datetime_obj, default=json_serial)