from datetime import datetime
from enum import Enum
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import ics
import pytz

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pacific_time(utc_time: datetime) -> datetime:
    pacific_tz = pytz.timezone("US/Pacific")
    return utc_time.astimezone(pacific_tz)


def convert_to_serialiable_json(json: dict) -> dict:
    return (
        {key: value.isoformat() if isinstance(value, datetime) else value for key, value in json.items()}
    )


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



class AgentId(str, Enum):
    johndoe = "johndoe" 
    janedoe = "janedoe"


app = FastAPI()


@app.get("/download-calendar/{agent_id}")
def download_calendar(agent_id: AgentId):
    ics_file_path = f"{agent_id.value}.ics"
    logger.info(f"Path: {ics_file_path}")

    if os.path.exists(ics_file_path):
        return FileResponse(ics_file_path, media_type="text/calendar", filename="calendar.ics")
    else:
        raise HTTPException(status_code=404, detail="Calendar file not found")


@app.get("/examine-calendar/{agent_id}")
def examine_calendar(agent_id: AgentId):
    ics_file_path = f"{agent_id.value}.ics"
    logger.info(f"Path: {ics_file_path}")

    sorted_calendar_events = parse_ics_file(ics_file_path)

    # Return the sorted, serializable list as JSON
    return JSONResponse(sorted_calendar_events)


