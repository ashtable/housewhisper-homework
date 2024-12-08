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
    availability_by_agent_id = dict()

    # Iterate through the ICS files for each agent
    for k, v in ics_config.items():
        # Create a new Dict to store agent_id k's availability by duration
        availability_by_agent_id[k] = dict()
        
        # Parse the events for agent_id k and sort events by start time
        sorted_events = read_ics_file_and_sort_events(v)
        
        # Get the first event in the current agent's calendar and then 
        # advance the pointer for iterating through the sorted list
        next_calendar_pointer = 0 if len(sorted_events) > 0 else None
        next_calendar_event = sorted_events[next_calendar_pointer] if next_calendar_pointer is not None else None
        next_calendar_pointer = next_calendar_pointer + 1 if len(sorted_events) > next_calendar_pointer + 1 else None

        # Keep a pointer to the prev calendar event as well
        prev_calendar_event = None

        # Iterate through every minute of every day 
        # to build out our fast in-memory lookup
        time_pointer = PREPROCESS_START
        while time_pointer <= PREPROCESS_END:
            # if time_pointer.date() == date(2024, 12, 6) and time_pointer.hour == 8:
            #     foo = "bar"

            # Case 1: It's outside of the business day
            # 
            # Result - The agent is unavailable, so we'll store a value of 0 min duration
            if time_pointer.hour < BUSINESS_DAY_START or time_pointer.hour >= BUSINESS_DAY_END:
                store_duration_for_hour_and_min(availability_by_agent_id[k], 0, time_pointer) 
            else:
                # Case 2: The next_calendar_event exists and has a begin datetime earlier than time_pointer
                #         and there is another calendar event after next_calendar_event
                #           
                # Result: Update prev_calendar_event, iterate next_calendar_event and advance next_calendar_pointer
                while next_calendar_event is not None and next_calendar_event["begin"] < time_pointer and next_calendar_pointer is not None:
                    prev_calendar_event = next_calendar_event
                    next_calendar_event = sorted_events[next_calendar_pointer] if next_calendar_pointer is not None else None
                    next_calendar_pointer = next_calendar_pointer + 1 if len(sorted_events) > next_calendar_pointer + 1 else None
                    
                # Case 3: The next_calendar_event is None (either when this loop started or due to Case 2 iterating)
                #         meaning that there are no more calendar events for this agent
                # OR    
                #
                # Case 4: The next_calendar_event has a begin datetime later than time_pointer
                #         and next_calendar_event is on a different/later date than time_pointer
                #
                # Result: The agent is free to meet for the rest of the current workday at this time
                if next_calendar_event is None or (
                    next_calendar_event["begin"] > time_pointer and next_calendar_event["begin"].date() != time_pointer.date()
                ):
                    time_pointer_date_at_5_pm = time_pointer.replace(hour=17, minute=0, second=0, microsecond=0)
                    minutes_free = abs((time_pointer_date_at_5_pm - time_pointer).total_seconds() / 60)
                    store_duration_for_hour_and_min(availability_by_agent_id[k], minutes_free, time_pointer)
                
                
                # Case 5: The next_calendar_event has a begin datetime before to time_pointer 
                #         the next_calendar_event overlaps with time_pointer
                #
                # Result: The agent is unavailable at this time, so store a duration value of 0
                elif (next_calendar_event is not None and (
                    next_calendar_event["begin"] < time_pointer and next_calendar_event["end"] > time_pointer
                )): 
                    store_duration_for_hour_and_min(availability_by_agent_id[k], 0, time_pointer)
                

                # Case 6: The next_calendar_event has a begin datetime equal to time_pointer in terms of date/hour/minute or
                #         the prev_calendar_event is not None and overlaps with time_pointer
                #
                # Result: The agent is unavailable at this time, so store a duration value of 0
                elif (next_calendar_event is not None and (
                    next_calendar_event["begin"].date() == time_pointer.date() and next_calendar_event["begin"].hour == time_pointer.hour and next_calendar_event["begin"].minute == time_pointer.minute
                ) or (prev_calendar_event is not None and (
                    prev_calendar_event["end"].date() == time_pointer.date() and prev_calendar_event["begin"] < time_pointer and prev_calendar_event["end"] > time_pointer 
                ))):
                    store_duration_for_hour_and_min(availability_by_agent_id[k], 0, time_pointer)
                    

                # Case 7: The next_calendar_event has a begin datetime later than time_pointer, 
                #         but on the same date as time_pointer.
                #
                # Result: The agent is free for the number of minutes between now and next_calendar_event
                elif next_calendar_event is not None and next_calendar_event["begin"] > time_pointer and next_calendar_event["begin"].date() == time_pointer.date():
                    minutes_free = abs((next_calendar_event["begin"] - time_pointer).total_seconds() / 60)
                    store_duration_for_hour_and_min(availability_by_agent_id[k], minutes_free, time_pointer)
                    
            # Add a minute to the loop counter
            time_pointer += timedelta(minutes=1) 

    # Return the availability        
    return availability_by_agent_id

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


def store_duration_for_hour_and_min(agent_availability: Dict, duration: int, appointment_time: datetime):
    if duration < 0 or agent_availability is None or appointment_time is None:
        raise ValueError("Invalid value for storage")

    appointment_date = appointment_time.date()
    appointment_hour = appointment_time.hour
    appointment_minute = appointment_time.minute

    # Initialize date's Dict lazily
    if appointment_date not in agent_availability:
        agent_availability[appointment_date] = dict()

    # Initialize hour's Dict lazily
    if appointment_hour not in agent_availability[appointment_date]:
        agent_availability[appointment_date][appointment_hour] = dict()

    # Save the duration's value in the innermost Dict
    agent_availability[appointment_date][appointment_hour][appointment_minute] = duration
