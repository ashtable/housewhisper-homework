from datetime import date, datetime, time, timedelta
from fastapi import FastAPI, HTTPException, Query
from typing import Annotated

from .constants import BUSINESS_DAY_START, BUSINESS_DAY_END, DEFAULT_TIMEZONE
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


@app.get("/query/{agent_id}/{duration}/{time_range_start_datetime_in_default_tz}/{time_range_end_datetime_in_default_tz}")
async def query(agent_id: int, duration: int, time_range_start_datetime_in_default_tz: datetime, time_range_end_datetime_in_default_tz: datetime):

    try:
        # Preprocess ICS files for query
        datastore = preprocess_ics_files(CONFIG)

        # List to store our return value
        available_times = []

        # Create a pointer to iterate through the datastore
        time_pointer = time_range_start_datetime_in_default_tz

        # Set time_pointer to the start of the following quarter-hour
        # so that we can suggest times at quarter-hour intervales
        if time_pointer.minute > 0:
            if time_pointer.minute < 15:
                time_pointer = time_pointer.replace(minute=15)
            elif time_pointer.minute < 30:
                time_pointer = time_pointer.replace(minute=30)
            elif time_pointer.minute < 45:
                time_pointer = time_pointer.replace(minute=45)
            else:
                time_pointer += timedelta(hours=1)
                time_pointer = time_pointer.replace(minute=0)

        # Iterate from time_range_start to time_range_end
        while time_pointer <= time_range_end_datetime_in_default_tz:
            print(f"Checking {time_pointer}")

            # Check for the agent's availability Dict
            if agent_id not in datastore:
                raise LookupError("Unable to find requested agent_id")
            
            # Check for the Date's availability Dict
            if time_pointer.date() not in datastore[agent_id]:
                raise LookupError("Unable to find requested nested Date Dict")

            # Check for the Hour's availability Dict
            if time_pointer.hour not in datastore[agent_id][time_pointer.date()]:
                raise LookupError("Unable to find requested nested Hour Dict")
                
            # Check for the Minutes's availability duratiion
            if time_pointer.minute not in datastore[agent_id][time_pointer.date()][time_pointer.hour]:
                raise LookupError("Unable to find requested nested Minute Duration")

            min_available = datastore[agent_id][time_pointer.date()][time_pointer.hour][time_pointer.minute]
            is_available = min_available >= duration

            if is_available:
                available_times.append(time_pointer)
 
            # Increment by quarter-hour increments
            time_pointer += timedelta(minutes=15)


        return {"available_times": available_times}
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))


@app.get("/multi-agent-coordination/{duration}/{time_range_start_datetime_in_default_tz}/{time_range_end_datetime_in_default_tz}")
async def coordinate(duration: int, time_range_start_datetime_in_default_tz: datetime, time_range_end_datetime_in_default_tz: datetime, agent_ids: Annotated[list[str] | None, Query()]):
    # List to store our return value
    available_times = []

    try:
        if agent_ids is None or len(agent_ids) < 2:
            raise ValueError("You must specify at least two agent_ids")

        # Preprocess ICS files for query
        datastore = preprocess_ics_files(CONFIG)

        # Create a Dict to store lists of when each specified agent is available
        agent_available_times = dict()
        for agent_id in agent_ids:
            # Convert to an int
            agent_id = int(agent_id)
            # Create a new list for the agent_id
            agent_available_times[agent_id] = []

        # Create a pointer to iterate through the datastore
        time_pointer = time_range_start_datetime_in_default_tz

        # Set time_pointer to the start of the following quarter-hour
        # so that we can suggest times at quarter-hour intervales
        if time_pointer.minute > 0:
            if time_pointer.minute < 15:
                time_pointer = time_pointer.replace(minute=15)
            elif time_pointer.minute < 30:
                time_pointer = time_pointer.replace(minute=30)
            elif time_pointer.minute < 45:
                time_pointer = time_pointer.replace(minute=45)
            else:
                time_pointer += timedelta(hours=1)
                time_pointer = time_pointer.replace(minute=0)

        # Iterate from time_range_start to time_range_end
        while time_pointer <= time_range_end_datetime_in_default_tz:
            print(f"Checking {time_pointer}")

            for agent_id in agent_ids:
                # Convert to an int
                agent_id = int(agent_id)

                # Check for the agent's availability Dict
                if agent_id not in datastore:
                    raise LookupError("Unable to find requested agent_id")
                
                # Check for the Date's availability Dict
                if time_pointer.date() not in datastore[agent_id]:
                    raise LookupError("Unable to find requested nested Date Dict")

                # Check for the Hour's availability Dict
                if time_pointer.hour not in datastore[agent_id][time_pointer.date()]:
                    raise LookupError("Unable to find requested nested Hour Dict")
                    
                # Check for the Minutes's availability duratiion
                if time_pointer.minute not in datastore[agent_id][time_pointer.date()][time_pointer.hour]:
                    raise LookupError("Unable to find requested nested Minute Duration")

                min_available = datastore[agent_id][time_pointer.date()][time_pointer.hour][time_pointer.minute]
                is_available = min_available >= duration

                if is_available:
                    agent_available_times[agent_id].append(time_pointer)
    
                # Increment by quarter-hour increments
                time_pointer += timedelta(minutes=15)

        available_times_set = None
        for agent_id in agent_ids:
            # Convert to an int
            agent_id = int(agent_id)

            if available_times_set is None:
                # For the first agent with available times, we accept all times and store them in a set
                available_times_list = agent_available_times[agent_id]
                available_times_set = set(available_times_list) if available_times_list is not None else None
            else:
                # For every other agent, we use set intersection to narrow the available_times_set 
                available_times_list = agent_available_times[agent_id]
                available_times_set = available_times_set.intersection(set(available_times_list))
        
        available_times = list(available_times_set)

        return {"available_times": available_times}
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))


@app.get("/underutilized/{agent_id}/{date_to_check}")
async def underutilized(agent_id: int, date_to_check: date):
    try:
        # Preprocess ICS files for query
        datastore = preprocess_ics_files(CONFIG)

        # List to store our return value
        available_times = []

        # Set the duration we'll check for to 60 so that we
        # only identify blocks of 1-hour or more as underutilized
        duration = 60

        # Create a pointer to iterate through the datastore
        # starting at the beginning of date_to_check
        time_pointer = datetime.combine(date_to_check, time(BUSINESS_DAY_START, 0), tzinfo=DEFAULT_TIMEZONE)
        time_pointer_end = datetime.combine(date_to_check, time(BUSINESS_DAY_END, 0), tzinfo=DEFAULT_TIMEZONE)

        # Set time_pointer to the start of the following quarter-hour
        # so that we can suggest times at quarter-hour intervales
        if time_pointer.minute > 0:
            if time_pointer.minute < 15:
                time_pointer = time_pointer.replace(minute=15)
            elif time_pointer.minute < 30:
                time_pointer = time_pointer.replace(minute=30)
            elif time_pointer.minute < 45:
                time_pointer = time_pointer.replace(minute=45)
            else:
                time_pointer += timedelta(hours=1)
                time_pointer = time_pointer.replace(minute=0)

        # Iterate from time_range_start to time_range_end
        while time_pointer <= time_pointer_end:
            print(f"Checking {time_pointer}")

            # Check for the agent's availability Dict
            if agent_id not in datastore:
                raise LookupError("Unable to find requested agent_id")
            
            # Check for the Date's availability Dict
            if time_pointer.date() not in datastore[agent_id]:
                raise LookupError("Unable to find requested nested Date Dict")

            # Check for the Hour's availability Dict
            if time_pointer.hour not in datastore[agent_id][time_pointer.date()]:
                raise LookupError("Unable to find requested nested Hour Dict")
                
            # Check for the Minutes's availability duratiion
            if time_pointer.minute not in datastore[agent_id][time_pointer.date()][time_pointer.hour]:
                raise LookupError("Unable to find requested nested Minute Duration")

            min_available = datastore[agent_id][time_pointer.date()][time_pointer.hour][time_pointer.minute]
            is_available = min_available >= duration

            if is_available:
                available_times.append(time_pointer)
 
            # Increment by quarter-hour increments
            time_pointer += timedelta(minutes=15)


        return {"available_times": available_times}
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))