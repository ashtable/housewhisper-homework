## To Run
1) Create a virtual environment and run `pip install -r requirements.txt`
2) Run `fastapi dev api.py`

## Endpoints
1) Download John Doe's Calendar: http://localhost:8000/download-calendar/johndoe
2) Examine John Doe's Calendar: http://localhost:8000/examine-calendar/johndoe
3) Check John Doe's Calendar: http://localhost:8000/check-calendar/johndoe/2024-12-02T19:00+00:00/2024-12-02T19:30+00:00
4) Query John Doe's Calendar: http://localhost:8000/query-calendar/johndoe/2024-12-02T17:00+00:00/2024-12-03T20:00+00:00/60
5) Multiagent Coordination: Ran out of time
6) Identify how busy the agent is on a specific day
