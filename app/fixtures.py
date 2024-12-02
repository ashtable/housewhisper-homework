from datetime import datetime
from ics import Calendar, Event
import pytest

from .constants import PACIFIC_TIMEZONE

###############################
# Create fixtures for testing #
###############################

@pytest.fixture(scope="session")
def ics_file_with_1_hour_event_at_12_pm_pacific_on_december_2_2024(tmp_path_factory):
    # Temporary directory for ics files
    temp_dir = tmp_path_factory.mktemp("ics_files")

    # Temporary filepath
    ics_file_path = temp_dir / "ics_file_with_1_hour_event_at_12_pm_pacific_on_december_2_2024"

    # Create an event
    event = Event()
    event.name = "Test Event at 12 pm pacific on 2024-12-02"
    event.begin = datetime(2024, 12, 2, 12, 0, tzinfo=PACIFIC_TIMEZONE)
    event.end = datetime(2024, 12, 2, 13, 0, tzinfo=PACIFIC_TIMEZONE)
     
    # Create a calendar with the event
    calendar = Calendar()
    calendar.events.add(event)

    # Write the .ics file to temporary directory
    with open(ics_file_path, "w") as file:
        file.writelines(calendar.serialize_iter())

    # Return the temporary filepath to the .ics file
    return ics_file_path
