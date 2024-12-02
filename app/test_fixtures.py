from datetime import datetime

from .constants import PACIFIC_TIMEZONE
from .fixtures import (
    ics_file_with_1_hour_event_at_12_pm_pacific_on_december_2_2024,
)
from .utils import read_ics_file_and_sort_events


#################################
# Create tests for the fixtures #
#################################

def test_ics_file_with_1_hour_event_at_12_pm_pacific_on_december_2_2024(
    ics_file_with_1_hour_event_at_12_pm_pacific_on_december_2_2024 
):
    ics_file_path = ics_file_with_1_hour_event_at_12_pm_pacific_on_december_2_2024

    # Assert that the temporary ICS file exists
    assert ics_file_path.exists()

    sorted_events = read_ics_file_and_sort_events(ics_file_path)

    assert len(sorted_events) == 1
    
    first_event = sorted_events[0]

    assert first_event.name == "Test Event at 12 pm pacific on 2024-12-02"
    assert first_event.begin == datetime(2024, 12, 2, 12, 0, tzinfo=PACIFIC_TIMEZONE)
    assert first_event.end == datetime(2024, 12, 2, 13, 0, tzinfo=PACIFIC_TIMEZONE)
