from datetime import datetime
from fastapi import FastAPI, HTTPException

from .utils import preprocess_ics_files


# We'll create a default set of calendars 
# for each of our agents that's mapped by 
# agent_id to ICS filename
CONFIG = {
    1: "janedoe.ics", 
    2: "jilldoe.ics", 
    3: "joedoe.ics", 
    4: "johndoe.ics", 
}

# We'll create an in-memory, key-value 
# datastore that we'll use to store the
# results of preprocessing ICS files
datastore = dict()

app = FastAPI()


@app.get("/check/{agent_id}/{duration}/{start_datetime_in_default_tz}")
async def check(agent_id: int, duration: int, start_datetime_in_default_tz: datetime):
    try:
        requested_time = start_datetime_in_default_tz

        # Preprocess ICS files for query
        datastore = preprocess_ics_files(CONFIG)

        # Check for the agent's availability Dict
        if agent_id not in datastore:
            raise LookupError("Unable to find requested agent_id")
        
        # Check for the Date's availability Dict
        if requested_time.date() not in datastore[agent_id]:
            raise LookupError("Unable to find requested nested Date Dict")

        # Check for the Hour's availability Dict
        if requested_time.hour not in datastore[agent_id][requested_time.date()]:
            raise LookupError("Unable to find requested nested Hour Dict")
            
        # Check for the Minutes's availability duratiion
        if requested_time.minute not in datastore[agent_id][requested_time.date()][requested_time.hour]:
            raise LookupError("Unable to find requested nested Minute Duration")

        min_available = datastore[agent_id][requested_time.date()][requested_time.hour][requested_time.minute]
        is_available = min_available >= duration
        response = "Yes, that meeting time is available!" if is_available else "Sorry, that meeting time is no longer available."

        return {"message": response}
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))