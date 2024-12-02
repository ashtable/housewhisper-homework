
## tl;dr

### Step 0) Clone this Repo

```git clone https://github.com/ashtable/housewhisper-homework.git```

### Step 1) Change directories

```cd housewhisper-homework```

### Step 2) Ensure you're using Python 3.12+

```python --version```

### Step 3) Create a virtual environment

```python3 -m venv .venv```

### Step 4) Activate the virtual environment 

```source .venv/bin/activate```

### Step 5) Install dependencies

```pip install -r requirements.txt```

### Step 6) Run the test suite

```pytest```

### Step 7) Run the web service in dev mode

```fastapi dev app/main.py```

## Sample Data in *.ics files in the repo
<img width="1194" alt="Screenshot 2024-12-02 at 12 27 43 PM" src="https://github.com/user-attachments/assets/7c96fe7b-a8d8-40fc-af0e-b2e02331f00c">


## Sample Requests:

### Check Endpoint

#### Check if Agent Jane Doe (agent_id == 1) is available for 60 minutes on Dec. 2nd, 2024 at 8:00 am Pacific Time:

##### Request
```http://localhost:8000/check/1/60/2024-12-02T08:00:00-08:00```

##### Response
`
{
    "message": "Yes, that meeting time is available!"
}
`

### Query Endpoint

#### Query when Agent Jane Doe (agent_id == 1) is available for 60 minutes between Dec. 2nd, 2024 from 8-10 am Pacific Time:

##### Request
```http://localhost:8000/query/1/60/2024-12-02T08:00:00-08:00/2024-12-02T10:00:00-08:00```

##### Response
`
{
    "available_times": [
        "2024-12-02T08:00:00-08:00",
        "2024-12-02T08:15:00-08:00",
        "2024-12-02T08:30:00-08:00",
        "2024-12-02T08:45:00-08:00",
        "2024-12-02T09:00:00-08:00"
    ]
}
`

### Multi-Agent-Coordination Endpoint

#### Query when Agents Jane Doe (agent_id == 1) and Jill Doe (agent_id == 2) are available for 60 minutes between Dec. 2nd, 2024 from 8-10 am Pacific Time:

##### Request
```http://localhost:8000/multi-agent-coordination/60/2024-12-02T08:00:00-08:00/2024-12-02T10:00:00-08:00?agent_ids=1&agent_ids=2```

##### Response
`
{
    "available_times": []
}
`

### Underutilized Endpoint 

#### Check when Agent Jane Doe (agent_id == 1) is underutilized on Dec. 2nd, 2024 and return 1-hour blocks when she is available

##### Request
```http://localhost:8000/underutilized/1/2024-12-02```

##### Response
`{
    "available_times": [
        "2024-12-02T08:00:00-08:00",
        "2024-12-02T08:15:00-08:00",
        "2024-12-02T08:30:00-08:00",
        "2024-12-02T08:45:00-08:00",
        "2024-12-02T09:00:00-08:00",
        "2024-12-02T15:00:00-08:00"
    ]
}
`

## Initial Design Diagrams

![HouseWhispser Homework Design - Page 1](https://github.com/user-attachments/assets/5ee978d4-e267-4f02-b284-c1e291e700d5)

![HouseWhispser Homework Design - Page 2](https://github.com/user-attachments/assets/ffe75e0a-1796-444d-80a9-4e7a5a000e12)
