from datetime import datetime
from zoneinfo import ZoneInfo


BUSINESS_DAY_START = 8
BUSINESS_DAY_END = 17

PACIFIC_TIMEZONE = tzinfo=ZoneInfo("America/Los_Angeles")

DEFAULT_TIMEZONE = PACIFIC_TIMEZONE

# These datetime values dictate the values that 
# are populated in the in-memory datastore
PREPROCESS_START = datetime(2024, 12, 2, 8, 0, tzinfo=PACIFIC_TIMEZONE)
PREPROCESS_END = datetime(2024, 12, 6, 17, 0, tzinfo=PACIFIC_TIMEZONE)