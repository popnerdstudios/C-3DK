from datetime import datetime
import pytz

def get_time(timezone_str="America/Los_Angeles"):
    try:
        timezone = pytz.timezone("America/Los_Angeles")
    except pytz.UnknownTimeZoneError:
        timezone = pytz.utc
    time = datetime.now(timezone)
    return time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
