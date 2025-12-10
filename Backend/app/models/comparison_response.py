from pydantic import BaseModel


class ForumsToxicity(BaseModel):
    forum_name: str
    average_toxicity: float
    platform: str  # '4chan' or 'reddit'
