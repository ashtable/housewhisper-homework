from datetime import datetime, time, timedelta
from enum import Enum
import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import FileResponse, JSONResponse
import ics
import pytz

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AgentId(str, Enum):
    johndoe = "johndoe" 
    janedoe = "janedoe"


def pacific_time(utc_time: datetime) -> datetime:
    pacific_tz = pytz.timezone("US/Pacific")
    return utc_time.astimezone(pacific_tz)


def convert_to_serialiable_json(json: dict) -> dict:
    return (
        {key: value.isoformat() if isinstance(value, datetime) else value for key, value in json.items()}
    )


def get_file_path(agent_id: AgentId) -> str:
   return f"{agent_id.value}.ics" 


def parse_ics_file(ics_file_path: str) -> list:
    # Read and parse the .ics file
    with open(ics_file_path, "r") as ics_file:
        calendar = ics.Calendar(ics_file.read())
    
    events = []
    
    # Iterate through the calendar's events
    for event in calendar.events:
        # Convert datetime fields to Pacific time and JSON-serializable formats
        events.append(
            convert_to_serialiable_json({
                "Event Name": event.name,
                "Start Time": datetime.fromisoformat(str(pacific_time(event.begin))),
                "End Time": datetime.fromisoformat(str(pacific_time(event.end))),
                "Description": event.description,
                "Location": event.location,
            })
        )

    # Sort the events in the calendar by Start Time and then Event Name
    events.sort(
        key=lambda x: (datetime.fromisoformat(str(x["Start Time"])), x["Event Name"])
    )

    return events


app = FastAPI()


@app.get("/download-calendar/{agent_id}")
def download_calendar(agent_id: AgentId):
    ics_file_path = get_file_path(agent_id)
    logger.info(f"Path: {ics_file_path}")

    if os.path.exists(ics_file_path):
        return FileResponse(ics_file_path, media_type="text/calendar", filename="calendar.ics")
    else:
        raise HTTPException(status_code=404, detail="Calendar file not found")


@app.get("/examine-calendar/{agent_id}")
def examine_calendar(agent_id: AgentId):
    ics_file_path = get_file_path(agent_id)
    logger.info(f"Path: {ics_file_path}")

    sorted_calendar_events = parse_ics_file(ics_file_path)

    # Return the sorted, serializable list as JSON
    return JSONResponse(sorted_calendar_events)


@app.get("/check-calendar/{agent_id}/{meeting_time_utc_start}/{meeting_time_utc_end}")
def check_calendar(agent_id: AgentId, meeting_time_utc_start: datetime, meeting_time_utc_end: datetime) -> bool:
    """Checks if an agent is available 
    for a meeting at the specified time."""

    ics_file_path = get_file_path(agent_id)
    logger.info(f"Path: {ics_file_path}")
    logger.info(f"Requested Start Time: {pacific_time(meeting_time_utc_start)}")
    logger.info(f"Requested End Time: {pacific_time(meeting_time_utc_end)}")

    sorted_calendar_events = parse_ics_file(ics_file_path) 

    for i in range(len(sorted_calendar_events)):
        event = sorted_calendar_events[i]
        event_start = datetime.fromisoformat(event['Start Time'])
        event_end = datetime.fromisoformat(event['End Time'])
        logger.debug(f"Event Start: {event_start}")
        logger.debug(f"Event End: {event_end}")

        if meeting_time_utc_end <= event_start:
            # Since we're iterating through a sorted list of events, if we 
            # come across an event that starts after the requested end time, 
            # we know we can fit it into the calendar and return True.
            return True
        elif meeting_time_utc_start < event_end and event_start < meeting_time_utc_end:
            # Similarly, if we come across an event in the calendar such 
            # that the event ends after the requested start time AND
            # the event starts before requested end time, we know that
            # we cannot fit it into the calendar and return False.
            return False

    # If we iterate through all of the events in the calendar without 
    # finding an event that starts after the requested meeting ends,
    # or an event that conflicts with the meeting time, we can conclude
    # that the meeting time is available and return True.
    return True


@app.get("/query-calendar/{agent_id}/{range_utc_start}/{range_utc_end}/{duration}")
def query_calendar(
    agent_id: AgentId, 
    range_utc_start: datetime, 
    range_utc_end: datetime, 
    duration: int = Path(..., ge=15, le=60)) -> List[datetime]:
    """Returns n available meeting times for an agent 
    given a set of time ranges and a duration."""

    ics_file_path = get_file_path(agent_id)
    logger.info(f"Path: {ics_file_path}")
    logger.info(f"Range Start Time: {pacific_time(range_utc_start)}")
    logger.info(f"Range End Time: {pacific_time(range_utc_end)}")
    logger.info(f"Duration: {duration}")

    sorted_calendar_events = parse_ics_file(ics_file_path) 

    # We'll calculate the number of days of available 
    # appointments to keep
    number_of_days = (range_utc_end - range_utc_start).days + 1

    # For checking day of the week
    monday = 0
    friday = 4

    possible_dates = dict()
    
    # We'll iterate through each day in the specified range
    # and assume that any weekday is an available meeting date
    start_date = range_utc_start.date()
    for i in range(number_of_days):
        calc_date = start_date + timedelta(days=i)
        if (calc_date.weekday() >= monday and calc_date.weekday() <= friday):
            possible_dates[str(calc_date)] = []


    # For checking the start and end of the day
    business_day_start_hour = 8
    business_day_start_min = business_day_start_hour * 60
    business_day_end_hour = 17 
    business_day_end_min = business_day_end_hour * 60


    for key in possible_dates:
        print(f"key: {key}")
        calc_date = datetime.strptime(key, "%Y-%m-%d").date()
        for start_min in range(business_day_start_min, business_day_end_min, 15):
            if (
                (start_min + duration) <= business_day_end_min
                and not (calc_date == range_utc_start.date() and start_min < pacific_time(range_utc_start).time().hour * 60 + pacific_time(range_utc_start).time().minute)
                and not (calc_date == range_utc_end.date() and start_min + duration > pacific_time(range_utc_end).time().hour * 60 + pacific_time(range_utc_end).time().minute)
                ):
                hour_part = start_min // 60
                min_part = start_min % 60
                possible_dates[key].append(datetime.combine(calc_date, time(hour_part, min_part)).isoformat())


    for i in range(len(sorted_calendar_events)):
        event = sorted_calendar_events[i]
        event_start = datetime.fromisoformat(event['Start Time'])
        event_end = datetime.fromisoformat(event['End Time'])
        logger.debug(f"Event Start: {event_start}")
        logger.debug(f"Event End: {event_end}")

        # We'll remove all overlapping meeting times
        for key in possible_dates:
            calc_date = datetime.strptime(key, "%Y-%m-%d").date()
            if calc_date == event_start.date() :
                for possible_time in possible_dates[key]:
                    possible_time_start = datetime.fromisoformat(possible_time)
                    possible_time_end = possible_time_start + timedelta(minutes=duration)
                    if possible_time_start.time() < event_end.time() and event_start.time() < possible_time_end.time():
                        possible_dates[key].remove(possible_time)

    return JSONResponse(convert_to_serialiable_json(possible_dates))
