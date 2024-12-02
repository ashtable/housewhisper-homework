from fastapi import FastAPI, HTTPException

from .utils import read_ics_file_and_sort_events


CONFIG = {
    1: "agent_janedoe.ics", 
    2: "agent_jilldoe.ics", 
    3: "agent_joedoe.ics", 
    4: "agent_johndoe.ics", 
}

app = FastAPI()


@app.get("/query")
async def query():
    return {"message": "Hello World"}
