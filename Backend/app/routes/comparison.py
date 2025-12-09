from fastapi import APIRouter, Query, HTTPException
from app.utils.plsql import PLSQL
from app.constants.queries import (
    SELECT_CHAN_ENGAGEMENT_BY_TYPE,
    SELECT_BOARD_COUNT,
)
from app.constants.reddit_queries import (
    SELECT_REDDIT_ENGAGEMENT_BY_TYPE,
    SELECT_SUBREDDIT_COUNT,
)
from app.models.chan import PlatformComparisonResponse, PlatformComparisonData
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime
import asyncio

router = APIRouter(prefix="/comparison", tags=["Platform Comparison"])
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

CHAN_DATABASE_URL = os.getenv("CHAN_DATABASE_URL")
REDDIT_DATABASE_URL = os.getenv("REDDIT_DATABASE_URL")


def sync_get_data(database_url, query):
    plsql = PLSQL(database_url)
    data = plsql.get_data_from(query)
    plsql.close_connection()
    return data


@router.get("/forums")
async def get_forums():
    chan_data, reddit_data = await asyncio.gather(
        asyncio.to_thread(sync_get_data, CHAN_DATABASE_URL, SELECT_BOARD_COUNT),
        asyncio.to_thread(sync_get_data, REDDIT_DATABASE_URL, SELECT_SUBREDDIT_COUNT),
    )

    return {
        "4chan_board_count": chan_data,
        "reddit_subreddit_count": reddit_data,
    }


@router.get("/engagement/by-type", response_model=PlatformComparisonResponse)
async def compare_engagement_by_type(
    board_name: str = Query(..., description="4chan board name (e.g., 'pol')"),
    subreddit: str = Query(..., description="Reddit subreddit name"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
):
    """
    Compare engagement metrics by post type across 4chan and Reddit (Graph 4A).
    Returns side-by-side comparison of average replies and thread counts.
    This directly answers RQ1 about platform differences in engagement patterns.
    """
    try:
        # Get 4chan data
        plsql_chan = PLSQL(CHAN_DATABASE_URL)
        chan_result = plsql_chan.get_data_from(
            SELECT_CHAN_ENGAGEMENT_BY_TYPE, (board_name, start_date, end_date)
        )
        plsql_chan.close_connection()

        # Convert dates to Unix timestamps for Reddit query
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())

        # Get Reddit data
        plsql_reddit = PLSQL(REDDIT_DATABASE_URL)
        reddit_result = plsql_reddit.get_data_from(
            SELECT_REDDIT_ENGAGEMENT_BY_TYPE, (subreddit, start_ts, end_ts)
        )
        plsql_reddit.close_connection()

        # Convert results to dictionaries for easy lookup
        chan_data = {
            row[0]: {
                "avg_replies": float(row[2]) if row[2] else 0.0,
                "total_threads": row[1],
            }
            for row in chan_result
        }
        reddit_data = {
            row[0]: {
                "avg_replies": float(row[2]) if row[2] else 0.0,
                "total_threads": row[1],
            }
            for row in reddit_result
        }

        # Combine data for all post types
        all_types = set(chan_data.keys()) | set(reddit_data.keys())

        comparison_data = []
        for post_type in sorted(all_types):
            comparison_data.append(
                PlatformComparisonData(
                    post_type=post_type,
                    chan_avg_replies=chan_data.get(post_type, {}).get("avg_replies"),
                    reddit_avg_replies=reddit_data.get(post_type, {}).get(
                        "avg_replies"
                    ),
                    chan_total_threads=chan_data.get(post_type, {}).get(
                        "total_threads"
                    ),
                    reddit_total_threads=reddit_data.get(post_type, {}).get(
                        "total_threads"
                    ),
                )
            )

        return PlatformComparisonResponse(
            chan_community=board_name,
            reddit_community=subreddit,
            start_date=start_date,
            end_date=end_date,
            data=comparison_data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
