from datetime import date, datetime
from ics import Calendar, Event
from pathlib import Path
from typing import Dict, List

from .constants import PREPROCESS_START, PREPROCESS_END

# Get the current working directory
cwd = Path.cwd()   

# Helper function to process the ics files specified 
# in the main.ICS_CONFIG dictionary and storing the
# contents in the returned Dict of Dicts
def preprocess_ics_files(ics_config: Dict[int, str]): # -> Dict[int, Dict[(date, int, int), bool]]:
    print("current dir")
    print(cwd)
    for k, v in ics_config.items():
        print(f"KEY: {k}, VALUE: {v}")
        sorted_events = read_ics_file_and_sort_events(v)
        print(sorted_events)

# Helper function to read an ICS file 
# and return a sorted list of events
def read_ics_file_and_sort_events(ics_file_path) -> List[Event]:
    with open(ics_file_path, "r") as file:
        calendar = Calendar(file.read())

    # Extract the events as a list
    events = list(calendar.events)

    # Sort the events by start time
    sorted_events = sorted(events, key=lambda event: event.begin)

    return sorted_events


