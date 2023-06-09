from typing import Dict, Generator, Iterable, Union, List
from datetime import date, datetime
from pathlib import Path
import json

DATETIMEFORMAT = "%Y-%m-%dT%H:%M:%S.%f"
DATEFORMAT = "%Y-%m-%d"
TIMELABELFORMAT = "%H:%M:%S"

class EventDay:
    """Collects all event ids for a given day"""

    def __init__(self, day: date):
        self.day = day
        self.events: List[int] = []

    def __eq__(self, o):
        return self.day.__eq__(o.day)

class OEvent:
    """Contains all event data
    Most important ones are:
    - comment: the actual text
    - id: the event id, used to load it from the dict of all events
    - datatime: the timestamp of the event
    """
    def __init__(self, filepath: str):
        self.json = json.load(open(filepath))
        self.datetime = datetime.strptime(self.json["date"], DATETIMEFORMAT)
        self.id = self.json["id"]
        self.comment = self.json["comment"]
        self.attachments = self.json["attachments"]

def events_from_folder(path: str) -> Dict[int, OEvent]:
    """Loads the events from a given cache folder

    Events must be present as JSON data, see Event.
    Attachments must be downloaded as corresponding file
    """
    events = {}
    for file in Path(path).iterdir():
        if file.suffix == ".json":
            event = OEvent(str(file.absolute()))
            events[event.id] = event
    return events

