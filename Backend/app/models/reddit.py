from pydantic import BaseModel
from typing import List, Optional


class SummaryStats(BaseModel):
    total_posts: int
    unique_subreddit: int
    total_toxicity: int
    total_comments: int


class EngagementByTypeData(BaseModel):
    post_type: str
    total_threads: int
    avg_replies: float
    total_replies: int
    avg_images: Optional[float] = None  # Only for 4chan


class EngagementByTypeResponse(BaseModel):
    platform: str  # "4chan" or "reddit"
    community: str  # board_name or subreddit
    start_date: str
    end_date: str
    data: List[EngagementByTypeData]


class DailyPostCountByDate(BaseModel):
    date: str
    subreddit_counts: dict[str, int]


class DailyPostCountsResponse(BaseModel):
    data: List[DailyPostCountByDate]
