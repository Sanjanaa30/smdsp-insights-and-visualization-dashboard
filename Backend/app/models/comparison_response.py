from pydantic import BaseModel
from typing import List

class ForumsToxicity(BaseModel):
    forum_name: str
    average_toxicity: float
    platform: str  # '4chan' or 'reddit'


class EventTimelinePoint(BaseModel):
    date: str
    count: int


class EventTimelineResponse(BaseModel):
    platform: str
    community: str
    event_date: str
    window: int
    timeline: List[EventTimelinePoint]
