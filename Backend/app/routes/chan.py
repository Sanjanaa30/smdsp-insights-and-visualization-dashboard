import os
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from app.constants.queries import (
    SELECT_ALL_BOARDS,
    SELECT_BOARD_TOXICITY,
    SELECT_CHAN_COUNTRY_STATS,
    SELECT_CHAN_DAILY_POST_COUNT,
    SELECT_CHAN_ENGAGEMENT_BY_TYPE,
    SELECT_CHAN_SUMMARY_STATS,
    SELECT_DAILY_ACTIVITY,
    SELECT_HOURLY_ACTIVITY,
)
from app.models.chan import (
    Board,
    CountryData,
    CountryStatsResponse,
    DailyActivityData,
    DailyActivityResponse,
    EngagementByTypeData,
    EngagementByTypeResponse,
    HourlyActivityData,
    HourlyActivityResponse,
    StatsDaily,
    SummaryStats,
)
from app.utils.logger import Logger
from app.utils.plsql import PLSQL
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/chan", tags=["4chan"])

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
CHAN_DATABASE_URL = os.getenv("CHAN_DATABASE_URL")
logger = Logger("logs").get_logger()


@router.get("/boards", response_model=List[Board])
async def get_boards():
    """Get list of all boards"""
    logger.info("GET /boards called")

    try:
        plsql = PLSQL(CHAN_DATABASE_URL)
        logger.info("Executing SELECT_ALL_BOARDS query")
        result = plsql.get_data_from(SELECT_ALL_BOARDS)
        logger.info(f"Query returned {len(result)} rows")

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
        logger.exception(f"Error in get_boards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary", response_model=SummaryStats)
async def get_summary_stats():
    logger.info("GET /stats/summary called")

    try:
        plsql = PLSQL(CHAN_DATABASE_URL)
        logger.info("Executing SELECT_CHAN_SUMMARY_STATS")

        result = plsql.get_data_from(SELECT_CHAN_SUMMARY_STATS, None)
        logger.info(f"Query returned {len(result)} rows")

        plsql.close_connection()

        if result:
            row = result[0]
            logger.info(f"Summary row: {row}")
            return SummaryStats(
                total_posts=row[0] or 0,
                unique_boards=row[1] or 0,
                total_toxicity=float(row[2]) if row[2] else 0.0,
            )
        else:
            logger.warning("Summary query returned empty results")
            return SummaryStats(total_posts=0, unique_boards=0, total_toxicity=0.0)

    except Exception as e:
        logger.exception(f"Error in get_summary_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/daily", response_model=List[StatsDaily])
async def get_daily_post_stats(
    board_name: Optional[str] = Query(None),
    start_date: Optional[str] = Query("2025-11-15"),
    end_date: Optional[str] = Query(None),
):
    logger.info(
        f"GET /stats/daily called with board_name={board_name}, start_date={start_date}, end_date={end_date}"
    )

    try:
        plsql = PLSQL(CHAN_DATABASE_URL)

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

        logger.info(f"Executing daily stats query: {sql}")
        logger.info(f"Query params: {params}")

        result = plsql.get_data_from(sql, tuple(params))
        logger.info(f"Query returned {len(result)} rows")

        plsql.close_connection()

        return [StatsDaily(day=str(row[0]), count=row[1]) for row in result]

    except Exception as e:
        logger.exception(f"Error in get_daily_post_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/posts")
async def debug_posts(board_name: str = Query("pol")):
    logger.info(f"GET /debug/posts called with board_name={board_name}")

    try:
        plsql = PLSQL(CHAN_DATABASE_URL)

        logger.info("Running debug test query for posts")

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

        params = (board_name, "2025-12-01", "2025-12-05")
        logger.info(f"Query params: {params}")

        result = plsql.get_data_from(test_query, params)
        logger.info(f"Debug returned {len(result)} rows")

        plsql.close_connection()

        return {
            "query_results": [
                {"date": str(row[0]), "type": row[1], "count": row[2]} for row in result
            ]
        }
    except Exception as e:
        logger.exception(f"Error in debug_posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity/daily", response_model=DailyActivityResponse)
async def get_daily_activity(board_name: str, start_date: str, end_date: str, post_types: Optional[List[str]] = None):
    logger.info(
        f"GET /activity/daily called with board={board_name}, start={start_date}, end={end_date}, post_types={post_types}"
    )

    try:
        plsql = PLSQL(CHAN_DATABASE_URL)
        logger.info("Executing SELECT_DAILY_ACTIVITY")

        result = plsql.get_data_from(
            SELECT_DAILY_ACTIVITY, (board_name, start_date, end_date)
        )
        logger.info(f"Query returned {len(result)} rows")

        plsql.close_connection()

        data = []
        for row in result:
            if post_types is None or row[1] in post_types:
                data.append(
                    DailyActivityData(
                        post_date=str(row[0]), post_type=row[1], post_count=row[2]
                    )
                )

        return DailyActivityResponse(
            board_name=board_name, start_date=start_date, end_date=end_date, data=data
        )

    except Exception as e:
        logger.exception(f"Error in get_daily_activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity/hourly", response_model=HourlyActivityResponse)
async def get_hourly_activity(board_name: str, selected_date: str, post_types: Optional[List[str]] = None):
    logger.info(
        f"GET /activity/hourly called with board={board_name}, date={selected_date}, post_types={post_types}"
    )

    try:
        plsql = PLSQL(CHAN_DATABASE_URL)

        logger.info("Executing SELECT_HOURLY_ACTIVITY")
        result = plsql.get_data_from(SELECT_HOURLY_ACTIVITY, (board_name, selected_date))
        logger.info(f"Query returned {len(result)} rows")

        plsql.close_connection()

        data = []
        for row in result:
            if post_types is None or row[2] in post_types:
                data.append(
                    HourlyActivityData(
                        post_date=str(row[0]),
                        hour=int(row[1]),
                        post_type=row[2],
                        post_count=row[3],
                    )
                )

        return HourlyActivityResponse(
            board_name=board_name, selected_date=selected_date, data=data
        )

    except Exception as e:
        logger.exception(f"Error in get_hourly_activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engagement/by-type", response_model=EngagementByTypeResponse)
async def get_engagement_by_type(board_name: str, start_date: str, end_date: str):
    logger.info(
        f"GET /engagement/by-type called with boards={board_name}, start={start_date}, end={end_date}"
    )

    try:
        board_list = [b.strip() for b in board_name.split(",") if b.strip()]
        logger.info(f"Parsed board list: {board_list}")

        plsql = PLSQL(CHAN_DATABASE_URL)
        logger.info("Executing SELECT_CHAN_ENGAGEMENT_BY_TYPE")

        result = plsql.get_data_from(
            SELECT_CHAN_ENGAGEMENT_BY_TYPE, (board_list, start_date, end_date)
        )
        logger.info(f"Query returned {len(result)} rows")

        plsql.close_connection()

        data = []

        for idx, row in enumerate(result):
            logger.debug(f"Row {idx}: {row}")
            if row and len(row) >= 5:
                data.append(
                    EngagementByTypeData(
                        post_type=row[0] or "unknown",
                        total_threads=row[1] or 0,
                        avg_replies=float(row[2] or 0),
                        avg_images=float(row[3] or 0),
                        total_replies=row[4] or 0,
                    )
                )
            else:
                logger.warning(f"Skipping malformed row {idx}: {row}")

        # Normalization logging
        if data:
            logger.info("Computing normalization values…")

        return EngagementByTypeResponse(
            platform="4chan",
            community=board_name,
            start_date=start_date,
            end_date=end_date,
            data=data,
        )

    except Exception as e:
        logger.exception(f"Error in get_engagement_by_type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/countries", response_model=CountryStatsResponse)
async def get_country_stats():
    logger.info("GET /stats/countries called")

    try:
        plsql = PLSQL(CHAN_DATABASE_URL)
        logger.info("Executing SELECT_CHAN_COUNTRY_STATS")

        result = plsql.get_data_from(SELECT_CHAN_COUNTRY_STATS, None)
        logger.info(f"Query returned {len(result)} rows")

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
        logger.exception(f"Error in get_country_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))