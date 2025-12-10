[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Ne05oVw_)

python -m uvicorn app.main:app --reload
pnpm dev --port 8080

http://localhost:8000/plots/forums
outpout
> 
    {
    "4chan_board_count": [
        [78]
    ],
    "reddit_subreddit_count": [
        [4386]
    ]
    }

# Get all boards
GET http://localhost:8000/chan/boards

# Get daily activity for /pol/ from Nov 1-14
GET http://localhost:8000/chan/activity/daily?board_name=pol&start_date=2025-11-01&end_date=2025-12-08

# Get hourly activity for Nov 14
GET http://localhost:8000/chan/activity/hourly?board_name=pol&selected_date=2025-12-04

# Filter by specific post types
GET http://localhost:8000/chan/activity/daily?board_name=pol&start_date=2025-11-01&end_date=2025-12-08&post_types=news&post_types=opinion

# 4chan Engagement 
GET http://localhost:8000/chan/engagement/by-type?board_name=pol&start_date=2025-12-01&end_date=2025-12-05

# Reddit Engagement 
http://localhost:8000/reddit/engagement/by-type?subreddit=geopolitics&start_timestamp=1760013696&end_timestamp=1761285425