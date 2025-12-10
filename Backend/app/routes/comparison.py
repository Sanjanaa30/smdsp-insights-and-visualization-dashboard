import asyncio
import os
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional

from app.constants.queries import (
    SELECT_BOARD_COUNT,
    SELECT_BOARD_TOXICITY,
    SELECT_CHAN_ENGAGEMENT_BY_TYPE,
    SELECT_CHAN_EVENT_RELATED,
    SELECT_CHAN_EVENT_RELATED_ALL,
)
from app.constants.reddit_queries import (
    SELECT_REDDIT_ENGAGEMENT_BY_TYPE,
    SELECT_REDDIT_EVENT_RELATED,
    SELECT_REDDIT_EVENT_RELATED_ALL,
    SELECT_SUBREDDIT_COUNT,
    SELECT_SUBREDDIT_TOXICITY,
)
from app.models.chan import PlatformComparisonData, PlatformComparisonResponse
from app.models.comparison_response import ForumsToxicity
from app.utils.plsql import PLSQL, get_data_db
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

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


@router.get("/top-toxic", response_model=List[ForumsToxicity])
async def get_top_toxic_forums():
    """
    Get top toxic forums from both 4chan and Reddit, sorted by average toxicity.
    Combines data from both platforms and returns a unified list.
    """
    try:
        chan_toxicity = get_data_db(CHAN_DATABASE_URL, SELECT_BOARD_TOXICITY, None)
        reddit_toxicity = get_data_db(
            REDDIT_DATABASE_URL, SELECT_SUBREDDIT_TOXICITY, None
        )

        final_result = []

        # Process 4chan toxicity
        if len(chan_toxicity) > 0:
            chan_scores = {}
            for board_name, toxicity in chan_toxicity:
                if toxicity is not None:
                    if board_name not in chan_scores:
                        chan_scores[board_name] = []
                    chan_scores[board_name].append(float(toxicity))

            for board_name, scores in chan_scores.items():
                avg = sum(scores) / len(scores)
                final_result.append(
                    ForumsToxicity(
                        forum_name=board_name,
                        average_toxicity=round(avg, 4),
                        platform="4chan",
                    )
                )

        # Process Reddit toxicity
        if len(reddit_toxicity) > 0:
            reddit_scores = {}
            for subreddit_name, toxicity in reddit_toxicity:
                if toxicity is not None:
                    if subreddit_name not in reddit_scores:
                        reddit_scores[subreddit_name] = []
                    reddit_scores[subreddit_name].append(float(toxicity))

            for subreddit_name, scores in reddit_scores.items():
                avg = sum(scores) / len(scores)
                final_result.append(
                    ForumsToxicity(
                        forum_name=subreddit_name,
                        average_toxicity=round(avg, 4),
                        platform="reddit",
                    )
                )

        # Sort by average toxicity descending
        final_result.sort(key=lambda x: x.average_toxicity, reverse=True)

        return final_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


CLOUDFLARE_KEYWORDS = [
    "cloudflare",
    "cloud flare",
    "cf outage",
    "cloudflare down",
    "cloudflare outage",
    "dns issue",
    "cloudflare dns",
    "cloudflare error",
    "cloudflare not working",
    "gateway timeout",
    "5xx",
    "error 500",
    "error 520",
    "error 522",
    # Added keywords
    "cloudflare service disruption",
    "cloudflare status",
    "cloudflare network issue",
    "cloudflare connectivity issue",
    "cloudflare routing issue",
    "cloudflare incident",
    "cloudflare downtime",
    "cloudflare problems",
    "cloudflare malfunction",
    "cloudflare crash",
    # DNS-related
    "cloudflare dns outage",
    "cloudflare dns down",
    "cloudflare dns failure",
    "cloudflare dns not responding",
    "dns resolving issue",
    "dns resolution failure",
    "dns lookup failed",
    "dns unavailable",
    "dns propagation issue",
    # Errors
    "cloudflare 5xx",
    "cloudflare 500 error",
    "cloudflare 502 bad gateway",
    "cloudflare 503 service unavailable",
    "cloudflare 504 gateway timeout",
    "cloudflare 524 timeout",
    "cloudflare 523 origin unreachable",
    "cloudflare 521 web server down",
    "origin server timeout",
    "server unreachable",
    # Performance & security issues
    "cloudflare rate limit",
    "cloudflare firewall error",
    "cloudflare ssl issue",
    "ssl handshake failed",
    "tls handshake failure",
    "connection timed out",
    "connection reset",
    "network congestion cloudflare",
    "ddos protection triggered",
    "cdn outage",
    "edge server issue",
    # Cloudflare services outages
    "cloudflare api down",
    "cloudflare workers issue",
    "cloudflare workers outage",
    "cloudflare pages outage",
    "cloudflare r2 outage",
    "cloudflare zero trust issue",
    "cloudflare tunnel down",
    "cloudflare warp not working",
    # User search phrases
    "why is cloudflare down",
    "cloudflare issues today",
    "cloudflare outage today",
    "sites down cloudflare",
    "website not loading cloudflare",
    "cannot connect via cloudflare",
    "websites timing out cf",
]


@router.get("/event-related-timeline")
async def get_event_related_timeline(
    platform: str, community: str = "", event_date: date = None, window: int = 7
):
    print("event_date", event_date)
    start_dt = event_date - timedelta(days=window)
    end_dt = event_date + timedelta(days=window)

    # Build LIKE patterns such as ["%cloudflare%", "%cf outage%", ...]
    patterns = [f"%{kw}%" for kw in CLOUDFLARE_KEYWORDS]
    start_ts = int(datetime.combine(start_dt, datetime.min.time()).timestamp())
    end_ts = int(datetime.combine(end_dt, datetime.min.time()).timestamp())
    # Reddit
    print(start_ts, end_ts)
    if platform == "reddit":
        # Parameters order: start_ts, end_ts (for date_series), then community, start, end, patterns (repeated for posts and comments)
        params = (
            start_ts,  # date_series start
            end_ts,  # date_series end
            community,
            start_ts,
            end_ts,
            patterns,
            community,
            start_ts,
            end_ts,
            patterns,
        )
        rows = get_data_db(REDDIT_DATABASE_URL, SELECT_REDDIT_EVENT_RELATED, params)

    # 4chan
    elif platform == "chan":
        # Parameters order: start_ts, end_ts (for date_series), then community, start, end, patterns (for subject), patterns (for comment)
        params = (start_ts, end_ts, community, start_ts, end_ts, patterns, patterns)
        rows = get_data_db(CHAN_DATABASE_URL, SELECT_CHAN_EVENT_RELATED, params)
    
    # Both platforms - need to merge results by date
    elif platform == "all" or platform == "":
        # Get Reddit data (all subreddits - no community filter)
        reddit_params = (
            start_ts,
            end_ts,
            start_ts,
            end_ts,
            patterns,
            start_ts,
            end_ts,
            patterns,
        )
        reddit_rows = get_data_db(REDDIT_DATABASE_URL, SELECT_REDDIT_EVENT_RELATED_ALL, reddit_params)
        
        # Get 4chan data (all boards - no community filter)
        chan_params = (start_ts, end_ts, start_ts, end_ts, patterns, patterns)
        chan_rows = get_data_db(CHAN_DATABASE_URL, SELECT_CHAN_EVENT_RELATED_ALL, chan_params)
        
        # Merge results by date - sum counts for same dates
        date_counts = {}
        for row in reddit_rows:
            date_key = row[0]
            date_counts[date_key] = date_counts.get(date_key, 0) + row[1]
        for row in chan_rows:
            date_key = row[0]
            date_counts[date_key] = date_counts.get(date_key, 0) + row[1]
        
        # Convert back to sorted list of tuples
        rows = sorted(date_counts.items(), key=lambda x: x[0])
    else:
        raise HTTPException(400, "Invalid platform")

    final_result = [{"date": str(row[0]), "count": row[1]} for row in rows]

    return {
        "platform": platform,
        "community": community,
        "event_date": str(event_date),
        "window": window,
        "timeline": final_result,
    }
