from fastapi.testclient import TestClient
from datetime import datetime
from ics import Calendar, Event
import pytest


from .main import app
from .utils import read_ics_file_and_sort_events



# Create a client for unit tests
client = TestClient(app)



#############################
# Query Endpoint Unit tests #
#############################

def test_query():
    response = client.get("/query")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
