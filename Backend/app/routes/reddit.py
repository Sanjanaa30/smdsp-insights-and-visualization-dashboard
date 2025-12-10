import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.constants.reddit_queries import (
    SELECT_ALL_SUBREDDITS,
    SELECT_DAILY_POST_COUNTS_BY_SUBREDDIT,
    SELECT_NUMBER_OF_SUBSCRIBERS,
    SELECT_REDDIT_ENGAGEMENT_BY_TYPE,
    SELECT_REDDIT_SUMMARY_STATS,
)
from app.models.reddit import (
    DailyPostCountByDate,
    DailyPostCountsResponse,
    EngagementByTypeData,
    EngagementByTypeResponse,
    SubScribers,
    SummaryStats,
)
from app.utils.plsql import PLSQL
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/reddit", tags=["Reddit"])
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

REDDIT_DATABASE_URL = os.getenv("REDDIT_DATABASE_URL")


@router.get("/subreddits")
async def get_subreddits():
    """Get list of available subreddits"""
    try:
        plsql = PLSQL(REDDIT_DATABASE_URL)
        query = """
        SELECT DISTINCT subreddit, COUNT(*) as post_count
        FROM posts
        GROUP BY subreddit
        ORDER BY post_count DESC
        LIMIT 20
        """
        result = plsql.get_data_from(query, ())
        plsql.close_connection()

        return {
            "subreddits": [{"name": row[0], "post_count": row[1]} for row in result]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/posts")
async def debug_posts(
    subreddit: str = Query("technology", description="Subreddit name"),
):
    """Debug endpoint to check Reddit posts data"""
    try:
        plsql = PLSQL(REDDIT_DATABASE_URL)

        # First check table structure
        structure_query = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'posts'
        ORDER BY ordinal_position
        """
        structure = plsql.get_data_from(structure_query, ())

        # Check all posts
        count_query = """
        SELECT COUNT(*) FROM posts
        """
        total = plsql.get_data_from(count_query, ())

        # Sample posts
        sample_query = """
        SELECT subreddit, unique_name, title, created_at
        FROM posts
        LIMIT 10
        """
        samples = plsql.get_data_from(sample_query, ())

        plsql.close_connection()

        return {
            "total_posts_in_db": total[0][0] if total else 0,
            "table_structure": [
                {"column": row[0], "type": row[1]} for row in structure
            ],
            "sample_posts": [
                {
                    "subreddit": row[0],
                    "unique_name": row[1],
                    "title": row[2][:50] if row[2] else None,
                    "created_at": str(row[3]),
                }
                for row in samples
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engagement/by-type", response_model=EngagementByTypeResponse)
async def get_engagement_by_type(
    subreddit: str = Query(..., description="Subreddit name"),
    start_timestamp: int = Query(..., description="Start Unix timestamp"),
    end_timestamp: int = Query(..., description="End Unix timestamp"),
):
    """
    Get average engagement metrics by post type (Graph 4A - Reddit).
    Returns average comments, total threads per post type.
    This directly answers RQ1 about how different post types affect engagement.
    """
    try:
        plsql = PLSQL(REDDIT_DATABASE_URL)
        result = plsql.get_data_from(
            SELECT_REDDIT_ENGAGEMENT_BY_TYPE,
            (subreddit, start_timestamp, end_timestamp),
        )
        plsql.close_connection()

        data = []
        for row in result:
            data.append(
                EngagementByTypeData(
                    post_type=row[0],
                    total_threads=row[1],
                    avg_replies=float(row[2]) if row[2] else 0.0,
                    total_replies=row[3],
                )
            )

        # Convert timestamps to date strings for display
        start_date = datetime.fromtimestamp(start_timestamp).strftime("%Y-%m-%d")
        end_date = datetime.fromtimestamp(end_timestamp).strftime("%Y-%m-%d")

        return EngagementByTypeResponse(
            platform="reddit",
            community=subreddit,
            start_date=start_date,
            end_date=end_date,
            data=data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary", response_model=SummaryStats)
async def get_summary_stats():
    """
    Get summary statistics: total posts, unique boards, and total toxicity.
    """
    try:
        plsql = PLSQL(REDDIT_DATABASE_URL)

        # Parameters for the query (board_name, start_date, end_date repeated twice)

        result = plsql.get_data_from(SELECT_REDDIT_SUMMARY_STATS, None)
        plsql.close_connection()
        # print(result)
        if result and len(result) > 0:
            row = result[0]
            return SummaryStats(
                total_posts=row[0] or 0,
                unique_subreddit=row[1] or 0,
                total_toxicity=float(row[2]) if row[2] else 0.0,
                total_comments=row[3] or 0,
            )
        else:
            return SummaryStats(
                total_posts=0, unique_subreddit=0, total_toxicity=0.0, total_comments=0
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts/daily-counts", response_model=DailyPostCountsResponse)
async def get_daily_post_counts(
    start_date: Optional[str] = Query(
        "2025-11-01", description="Start date in YYYY-MM-DD format"
    ),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
):
    """
    Get daily post counts by subreddit with optional date filtering.
    Returns counts of posts grouped by subreddit and date.

    Args:
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)

    Returns:
        List of daily post counts with subreddit_name, date, and counts
    """
    try:
        # Build dynamic date filter
        date_filter = ""
        params = []

        if start_date:
            # Validate date format
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                date_filter += " AND DATE(TO_TIMESTAMP(created_at)) >= %s"
                params.append(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD"
                )

        if end_date:
            # Validate date format
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
                date_filter += " AND DATE(TO_TIMESTAMP(created_at)) <= %s"
                params.append(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD"
                )

        # Build final query
        query = SELECT_DAILY_POST_COUNTS_BY_SUBREDDIT.format(date_filter=date_filter)

        plsql = PLSQL(REDDIT_DATABASE_URL)
        result = plsql.get_data_from(query, tuple(params))
        plsql.close_connection()

        # Group data by date
        date_groups = {}
        for row in result:
            date = str(row[0])
            subreddit_name = row[1]
            count = row[2]

            if date not in date_groups:
                date_groups[date] = {}

            date_groups[date][subreddit_name] = count

        # Convert to response format
        data = [
            DailyPostCountByDate(date=date, subreddit_counts=counts)
            for date, counts in sorted(date_groups.items())
        ]

        return DailyPostCountsResponse(data=data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subreddit/top-subscribers", response_model=List[SubScribers])
async def get_top_subscribers():
    try:
        plsql = PLSQL(REDDIT_DATABASE_URL)
        result = plsql.get_data_from(SELECT_NUMBER_OF_SUBSCRIBERS, None)
        plsql.close_connection()
        if len(result) > 0:
            final_result = []
            for subreddit_name, subscribers in result:
                if subreddit_name.lower().startswith("r/"):
                    subreddit_name = subreddit_name[2:]
                elif subreddit_name.lower().startswith("/r/"):
                    subreddit_name = subreddit_name[3:]
                subreddit_name = subreddit_name[0].upper() + subreddit_name[1:]
                final_result.append(
                    SubScribers(subreddit_name=subreddit_name, subscribers=subscribers)
                )
            return final_result
        else:
            return SubScribers(subreddit_name=0, subscribers=0)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

