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


@app.get("/query")
async def query():
    # Preprocess ICS files for query
    datastore = preprocess_ics_files(CONFIG)

    return {"message": "Hello World"}
