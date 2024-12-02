from ics import Calendar


# Helper function to read an ICS file 
# and return a sorted list of events
def read_ics_file_and_sort_events(ics_file_path):
    with open(ics_file_path, "r") as file:
        calendar = Calendar(file.read())

    # Extract the events as a list
    events = list(calendar.events)

    # Sort the events by start time
    sorted_events = sorted(events, key=lambda event: event.begin)

    return sorted_events

