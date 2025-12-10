from fastapi import APIRouter, Query, HTTPException
from app.utils.plsql import PLSQL
from app.constants.queries import (
    SELECT_BOARD_TOXICITY,
    SELECT_DAILY_ACTIVITY,
    SELECT_HOURLY_ACTIVITY,
    SELECT_ALL_BOARDS,
    SELECT_CHAN_ENGAGEMENT_BY_TYPE,
    SELECT_CHAN_DAILY_POST_COUNT,
    SELECT_CHAN_SUMMARY_STATS,
    SELECT_CHAN_COUNTRY_STATS,
)
from app.models.chan import (
    DailyActivityResponse,
    DailyActivityData,
    HourlyActivityResponse,
    HourlyActivityData,
    Board,
    EngagementByTypeResponse,
    EngagementByTypeData,
    StatsDaily,
    SummaryStats,
    CountryData,
    CountryStatsResponse,
)
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime, date

router = APIRouter(prefix="/chan", tags=["4chan"])
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

CHAN_DATABASE_URL = os.getenv("CHAN_DATABASE_URL")


@router.get("/boards", response_model=List[Board])
async def get_boards():
    """Get list of all boards"""
    try:
        plsql = PLSQL(CHAN_DATABASE_URL)
        result = plsql.get_data_from(SELECT_ALL_BOARDS)
        plsql.close_connection()

        boards = []
        for row in result:
            boards.append(
                {
                    "board_code": row[0],
                    "board_title": row[1],
                    "meta_description": row[2],
                    "ws_board": row[3],
                }
            )
        return boards
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary", response_model=SummaryStats)
async def get_summary_stats():
    """
    Get summary statistics: total posts, unique boards, and total toxicity.
    """
    try:
        plsql = PLSQL(CHAN_DATABASE_URL)

        # Parameters for the query (board_name, start_date, end_date repeated twice)

        result = plsql.get_data_from(SELECT_CHAN_SUMMARY_STATS, None)
        plsql.close_connection()
        print(result)
        if result and len(result) > 0:
            row = result[0]
            return SummaryStats(
                total_posts=row[0] or 0,
                unique_boards=row[1] or 0,
                total_toxicity=float(row[2]) if row[2] else 0.0,
            )
        else:
            return SummaryStats(total_posts=0, unique_boards=0, total_toxicity=0.0)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/daily", response_model=List[StatsDaily])
async def get_daily_post_stats(
    board_name: Optional[str] = Query(None, description="Board name (e.g., 'pol')"),
    start_date: Optional[str] = Query(
        "2025-11-15", description="Start date YYYY-MM-DD"
    ),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
):
    """
    Get daily post counts.
    If board_name is omitted → include all boards.
    If start_date or end_date omitted → ignore that bound.
    """
    try:
        plsql = PLSQL(CHAN_DATABASE_URL)

        # Build dynamic query using created_at timestamp column
        sql = SELECT_CHAN_DAILY_POST_COUNT

        params = []

        if board_name:
            sql += " AND board_name = %s"
            params.append(board_name)

        if start_date:
            sql += " AND created_at >= %s::timestamp"
            params.append(start_date)

        if end_date:
            sql += " AND created_at < (%s::timestamp + interval '1 day')"
            params.append(end_date)

        sql += """
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """

        result = plsql.get_data_from(sql, tuple(params))
        plsql.close_connection()

        return [StatsDaily(day=str(row[0]), count=row[1]) for row in result]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/posts")
async def debug_posts(board_name: str = Query("pol", description="Board name")):
    """Debug endpoint to check posts data"""
    try:
        plsql = PLSQL(CHAN_DATABASE_URL)

        # Test the exact query from SELECT_DAILY_ACTIVITY
        test_query = """
        SELECT 
            DATE(to_timestamp(post_time)) as post_date,
            CASE 
                WHEN COALESCE(comment, '') ILIKE '%%?%%' THEN 'question'
                WHEN COALESCE(comment, '') ILIKE '%%news%%' OR COALESCE(comment, '') ILIKE '%%breaking%%' THEN 'news'
                WHEN filename IS NOT NULL AND ext IN ('.jpg', '.png', '.gif') THEN 'meme'
                ELSE 'opinion'
            END as post_type,
            COUNT(*) as post_count
        FROM posts
        WHERE board_name = %s
            AND to_timestamp(post_time) >= %s::timestamp
            AND to_timestamp(post_time) < (%s::timestamp + interval '1 day')
            AND resto = 0
        GROUP BY post_date, post_type
        ORDER BY post_date, post_type
        LIMIT 20
        """
        result = plsql.get_data_from(
            test_query, (board_name, "2025-12-01", "2025-12-05")
        )

        plsql.close_connection()

        return {
            "query_results": [
                {"date": str(row[0]), "type": row[1], "count": row[2]} for row in result
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity/daily", response_model=DailyActivityResponse)
async def get_daily_activity(
    board_name: str = Query(..., description="Board name (e.g., 'pol')"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    post_types: Optional[List[str]] = Query(
        None, description="Filter by post types: question, opinion, news, meme"
    ),
):
    """
    Get daily activity data for a board (Graph 1A).
    Returns post counts per day grouped by post type.
    """
    try:
        plsql = PLSQL(CHAN_DATABASE_URL)
        result = plsql.get_data_from(
            SELECT_DAILY_ACTIVITY, (board_name, start_date, end_date)
        )
        plsql.close_connection()

        data = []
        for row in result:
            post_type = row[1]
            # Filter by post types if specified
            if post_types is None or post_type in post_types:
                data.append(
                    DailyActivityData(
                        post_date=str(row[0]), post_type=post_type, post_count=row[2]
                    )
                )

        return DailyActivityResponse(
            board_name=board_name, start_date=start_date, end_date=end_date, data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity/hourly", response_model=HourlyActivityResponse)
async def get_hourly_activity(
    board_name: str = Query(..., description="Board name (e.g., 'pol')"),
    selected_date: str = Query(..., description="Selected date in YYYY-MM-DD format"),
    post_types: Optional[List[str]] = Query(
        None, description="Filter by post types: question, opinion, news, meme"
    ),
):
    """
    Get hourly activity data for a specific day (Graph 1B).
    Returns post counts per hour grouped by post type.
    """
    try:
        plsql = PLSQL(CHAN_DATABASE_URL)
        result = plsql.get_data_from(
            SELECT_HOURLY_ACTIVITY, (board_name, selected_date)
        )
        plsql.close_connection()

        data = []
        for row in result:
            post_type = row[2]
            # Filter by post types if specified
            if post_types is None or post_type in post_types:
                data.append(
                    HourlyActivityData(
                        post_date=str(row[0]),
                        hour=int(row[1]),
                        post_type=post_type,
                        post_count=row[3],
                    )
                )

        return HourlyActivityResponse(
            board_name=board_name, selected_date=selected_date, data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engagement/by-type", response_model=EngagementByTypeResponse)
async def get_engagement_by_type(
    board_name: str = Query("pol,g,sp,int,out", description="Comma-separated board names (e.g., 'pol,g,int')"),
    start_date: str = Query(
        "2025-11-01", description="Start date in YYYY-MM-DD format"
    ),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
):
    """
    Get average engagement metrics by post type (Graph 4A - 4chan).
    Returns average replies, total threads, and total replies per post type.
    This directly answers RQ1 about how different post types affect engagement.
    """
    try:
        # Parse comma-separated board names into a list
        board_list = [b.strip() for b in board_name.split(",") if b.strip()]
        
        plsql = PLSQL(CHAN_DATABASE_URL)
        result = plsql.get_data_from(
            SELECT_CHAN_ENGAGEMENT_BY_TYPE, (board_list, start_date, end_date)
        )
        plsql.close_connection()

        data = []
        print(f"Query returned {len(result)} rows")
        for idx, row in enumerate(result):
            if row is None:
                print(f"Row {idx} is None, skipping")
                continue

            # Check row length
            if len(row) < 5:
                print(f"Row {idx} has only {len(row)} columns: {row}")
                continue

            print(f"Row {idx}: {row}")
            data.append(
                EngagementByTypeData(
                    post_type=row[0] if row[0] else "unknown",
                    total_threads=row[1] if row[1] is not None else 0,
                    avg_replies=float(row[2]) if row[2] is not None else 0.0,
                    avg_images=float(row[3]) if row[3] is not None else 0.0,
                    total_replies=row[4] if row[4] is not None else 0,
                )
            )
        if data:  # avoid division by zero if empty
            max_threads = max(d.total_threads for d in data)
            max_replies = max(d.total_replies for d in data)
            max_avg_replies = max(d.avg_replies for d in data)
            max_avg_images = max(d.avg_images for d in data)

            for d in data:
                d.norm_total_threads = (
                    d.total_threads / max_threads if max_threads else 0
                )
                d.norm_total_replies = (
                    d.total_replies / max_replies if max_replies else 0
                )
                d.norm_avg_replies = (
                    d.avg_replies / max_avg_replies if max_avg_replies else 0
                )
                d.norm_avg_images = (
                    d.avg_images / max_avg_images if max_avg_images else 0
                )

        return EngagementByTypeResponse(
            platform="4chan",
            community=board_name,
            start_date=start_date,
            end_date=end_date,
            data=data,
        )
    except Exception as e:
        print(f"Error in get_engagement_by_type: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/countries", response_model=CountryStatsResponse)
async def get_country_stats():
    """
    Get country statistics from posts table.
    Returns country names with their post counts, percentages, and flags.
    """
    try:
        plsql = PLSQL(CHAN_DATABASE_URL)

        result = plsql.get_data_from(SELECT_CHAN_COUNTRY_STATS, None)
        plsql.close_connection()

        data = []
        for row in result:
            data.append(
                CountryData(
                    name="Unknown" if len(row[0]) < 1 else row[0],
                    count=row[1],
                    percent=float(row[2]),
                    flag=row[3],
                )
            )

        return CountryStatsResponse(data=data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
