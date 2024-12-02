from datetime import date, datetime, timedelta
from ics import Calendar, Event
from typing import Dict, List

from .constants import (
    BUSINESS_DAY_START,
    BUSINESS_DAY_END,
    DEFAULT_TIMEZONE,
    PREPROCESS_START,
    PREPROCESS_END,
)


# Helper function to process the ics files specified 
# in the main.ICS_CONFIG dictionary and storing the
# contents in the returned Dict of Dicts
def preprocess_ics_files(ics_config: Dict[int, str]): # -> Dict[int, Dict[(date, int, int), bool]]:
    # Iterate through the ICS files for each agent
    for k, v in ics_config.items():
        print(f"KEY: {k}, VALUE: {v}")
        # Parse the events and sort by start time
        sorted_events = read_ics_file_and_sort_events(v)
        print(sorted_events)
        # Iterate through every minute of every day 
        # to build out our fast in-memory lookup
        # time_pointer = PREPROCESS_START
        # while time_pointer <= PREPROCESS_END:
        #     print(time_pointer.hour)
        #     print(time_pointer.minute)

        

# Helper function to read an ICS file 
# and return a sorted list of events
def read_ics_file_and_sort_events(ics_file_path) -> List[Event]:
    with open(ics_file_path, "r") as file:
        calendar = Calendar(file.read())

    # Extract the events as a list
    events = []
    
    for event in calendar.events:
        # Convert the begin/end datetime values to the Default/Pacific timezone
        start_pacific = event.begin.astimezone(DEFAULT_TIMEZONE)
        end_pacific = event.end.astimezone(DEFAULT_TIMEZONE)
        
        # Append the event data to the list
        events.append({
            "name": event.name,
            "begin": start_pacific,
            "end": end_pacific,
            "description": event.description,
            "location": event.location,
        })

    # Sort the events by start time
    sorted_events = sorted(events, key=lambda e: e["begin"])

    return sorted_events


