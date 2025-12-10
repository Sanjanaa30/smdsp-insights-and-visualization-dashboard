from pydantic import BaseModel
from typing import List, Optional


class StatsDaily(BaseModel):
    day: str
    count: int


class SummaryStats(BaseModel):
    total_posts: int
    unique_boards: int
    total_toxicity: int


class DailyActivityData(BaseModel):
    post_date: str
    post_type: str
    post_count: int


class DailyActivityResponse(BaseModel):
    board_name: str
    start_date: str
    end_date: str
    data: List[DailyActivityData]


class HourlyActivityData(BaseModel):
    post_date: str
    hour: int
    post_type: str
    post_count: int


class HourlyActivityResponse(BaseModel):
    board_name: str
    selected_date: str
    data: List[HourlyActivityData]


class Board(BaseModel):
    board_code: str
    board_title: str
    meta_description: Optional[str]
    ws_board: int


class EngagementByTypeData(BaseModel):
    post_type: str
    total_threads: float
    avg_replies: float
    total_replies: float
    avg_images: Optional[float] = None  # Only for 4chan
    norm_total_threads: Optional[float] = None
    norm_total_replies: Optional[float] = None
    norm_avg_replies: Optional[float] = None
    norm_avg_images: Optional[float] = None


class EngagementByTypeResponse(BaseModel):
    platform: str  # "4chan" or "reddit"
    community: str  # board_name or subreddit
    start_date: str
    end_date: str
    data: List[EngagementByTypeData]


class PlatformComparisonData(BaseModel):
    post_type: str
    chan_avg_replies: Optional[float]
    reddit_avg_replies: Optional[float]
    chan_total_threads: Optional[int]
    reddit_total_threads: Optional[int]


class PlatformComparisonResponse(BaseModel):
    chan_community: str
    reddit_community: str
    start_date: str
    end_date: str
    data: List[PlatformComparisonData]


class CountryData(BaseModel):
    name: str
    count: int
    percent: float
    flag: str


class CountryStatsResponse(BaseModel):
    data: List[CountryData]
