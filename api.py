from enum import Enum
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse


class AgentId(str, Enum):
    johndoe = "johndoe" 
    janedoe = "janedoe"


app = FastAPI()


@app.get("/download-calendar/{agent_id}")
async def download_calendar(agent_id: AgentId):

    ics_file_path = f"{agent_id.value}.ics"
    print(f"Path: {ics_file_path}")

    if os.path.exists(ics_file_path):
        return FileResponse(ics_file_path, media_type="text/calendar", filename="calendar.ics")
    else:
        raise HTTPException(status_code=404, detail="Calendar file not found")


