from fastapi.testclient import TestClient
from datetime import datetime
from ics import Calendar, Event
import pytest
from zoneinfo import ZoneInfo

from .main import app

# Create a Timezone Info object for Pacific Time
PACIFIC_TIMEZONE = tzinfo=ZoneInfo("America/Los_Angeles")

# Create a client for unit tests
client = TestClient(app)


# Helper function to read an ICS file 
# and return a sorted list of events
def read_ics_file_and_sort_events(ics_file_path):
    with open(ics_file_path, "r") as file:
        calendar = Calendar(file.read())

    # Extract the events as a list
    events = list(calendar.events)

    # Sort the events by start time
    sorted_events = sorted(events, key=lambda event: event.begin)

    return sorted_events


############################################################
# Create fixtures for testing, with tests for each fixture #
############################################################

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


#############################
# Query Endpoint Unit tests #
#############################

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
