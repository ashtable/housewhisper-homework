from datetime import datetime
from enum import Enum
import logging
import os

from fastapi import FastAPI, HTTPException
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
    """Checks if an agent is available for 
    a 1-hour meeting at the specified time"""

    ics_file_path = get_file_path(agent_id)
    logger.info(f"Path: {ics_file_path}")
    logger.info(f"Requested Start Time: {pacific_time(meeting_time_utc_start)}")
    logger.info(f"Requested End Time: {pacific_time(meeting_time_utc_end)}")


    requested_start = meeting_time_utc_start
    requested_end = meeting_time_utc_end

    sorted_calendar_events = parse_ics_file(ics_file_path) 

    for i in range(len(sorted_calendar_events)):
        event = sorted_calendar_events[i]
        event_start = datetime.fromisoformat(event['Start Time'])
        event_end = datetime.fromisoformat(event['End Time'])
        logger.debug(f"Event Start: {event_start}")
        logger.debug(f"Event End: {event_end}")

        if requested_end <= event_start:
            # Since we're iterating through a sorted list of events, if we 
            # come across an event that starts after the requested end time, 
            # we know we can fit it into the calendar and return True.
            return True
        elif requested_start < event_end and event_start < requested_end:
            # Similarly, if we come across an event in the calendar such 
            # that the event ends after the requested start time AND
            # the event starts before requested end time, we know that
            # we cannot fit it into the calendar and return False.
            return False


    return True