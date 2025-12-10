# 4CHAN
SELECT_BOARD_COUNT = "SELECT count(distinct(board_code)) FROM boards"

SELECT_CHAN_DAILY_POST_COUNT = """
SELECT 
    DATE(created_at) AS day, 
    COUNT(*) AS posts 
FROM posts 
WHERE 1=1
"""

# Summary statistics query
SELECT_CHAN_SUMMARY_STATS = """
SELECT 
    COUNT(*) AS total_posts,
    COUNT(DISTINCT board_name) AS unique_boards,
    (SELECT COUNT(*) FROM toxicity) AS total_toxicity
FROM posts;
"""

# Activity Explorer - Daily Activity (Graph 1A)
SELECT_DAILY_ACTIVITY = """
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
"""

# Activity Explorer - Hourly Activity (Graph 1B)
SELECT_HOURLY_ACTIVITY = """
SELECT 
    DATE(to_timestamp(post_time)) as post_date,
    EXTRACT(HOUR FROM to_timestamp(post_time)) as hour,
    CASE 
        WHEN COALESCE(comment, '') ILIKE '%%?%%' THEN 'question'
        WHEN COALESCE(comment, '') ILIKE '%%news%%' OR COALESCE(comment, '') ILIKE '%%breaking%%' THEN 'news'
        WHEN filename IS NOT NULL AND ext IN ('.jpg', '.png', '.gif') THEN 'meme'
        ELSE 'opinion'
    END as post_type,
    COUNT(*) as post_count
FROM posts
WHERE board_name = %s
    AND DATE(to_timestamp(post_time)) = %s::date
    AND resto = 0
GROUP BY post_date, hour, post_type
ORDER BY hour, post_type
"""

# Get list of boards
SELECT_ALL_BOARDS = """
SELECT board_code, board_title, meta_description, ws_board
FROM boards
ORDER BY board_code
"""

# Country Statistics
SELECT_CHAN_COUNTRY_STATS = """
SELECT 
    country_name AS name,
    COUNT(*) AS count,
    ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()), 2) AS percent,
    country AS flag   -- use stored country code instead of emoji
FROM posts
GROUP BY country_name, country
ORDER BY count DESC
LIMIT 7
"""

# Engagement by Post Type (Graph 4A) - 4chan
SELECT_CHAN_ENGAGEMENT_BY_TYPE = """
SELECT
    post_type,
    COUNT(*) AS total_threads,
    AVG(reply_count) AS avg_replies,
    AVG(image_count) AS avg_images,
    SUM(reply_count) AS total_replies
FROM (
    SELECT
        p.post_no,

        /* ---- Enhanced Post-Type Classification ---- */
        CASE 
            /* Strong question detection */
            WHEN LOWER(p.comment) ~ '\?$'
              OR LOWER(p.comment) LIKE '%%why%%'
              OR LOWER(p.comment) LIKE '%%how%%'
              OR LOWER(p.comment) LIKE '%%what do you think%%'
              OR LOWER(p.comment) LIKE '%%is it true%%'
              OR LOWER(p.comment) LIKE '%%should i%%'
            THEN 'Question'

            /* News — now detects more keywords */
            WHEN LOWER(p.comment) LIKE ANY (ARRAY[
                '%%news%%', '%%breaking%%', '%%breaking news%%', '%%report%%', '%%reported%%', 
                '%%journalist%%', '%%update%%', '%%press%%', '%%headline%%', '%%alert%%', '%%source:%%'
            ])
            THEN 'News'

            /* Meme classification — more robust */
            WHEN p.filename IS NOT NULL AND p.ext IN ('.jpg', '.png', '.gif', '.jpeg')
                 OR LOWER(p.comment) LIKE ANY (ARRAY[
                     '%%meme%%', '%%dank%%', '%%lol%%', '%%funny%%', '%%cope%%', '%%cringe%%', '%%based%%'
                 ])
            THEN 'Meme'

            /* Opinion — fallback, but expanded keyword detection */
            WHEN LOWER(p.comment) LIKE ANY (ARRAY[
                '%%i think%%', '%%in my opinion%%', '%%imo%%', '%%my view%%', '%%my take%%', '%%i believe%%',
                '%%it seems to me%%', '%%i feel like%%', '%%personally%%'
            ])
            THEN 'Opinion'

            /* Default bucket */
            ELSE 'Opinion'
        END AS post_type,

        /* Replies + Image Count */
        COUNT(r.post_no) AS reply_count,
        p.images AS image_count

    FROM posts p
    LEFT JOIN posts r ON r.resto = p.post_no

    WHERE 
        p.resto = 0
        AND p.board_name = ANY(%s)
        AND to_timestamp(p.post_time) >= %s::timestamp
        AND to_timestamp(p.post_time) < (%s::timestamp + interval '1 day')

    GROUP BY p.post_no, post_type, p.images
) t
GROUP BY post_type
ORDER BY post_type;
"""

# Get Average Toxicity by Subreddit
SELECT_BOARD_TOXICITY = """
SELECT board_name, toxicity FROM toxicity WHERE toxicity IS NOT NULL
"""

# Event-related posts timeline for 4chan
# Uses created_at (TIMESTAMP) column for date filtering
# Generates complete date series to show 0 counts for days without matches
SELECT_CHAN_EVENT_RELATED = """
WITH date_series AS (
    SELECT generate_series(
        DATE(TO_TIMESTAMP(%s)),
        DATE(TO_TIMESTAMP(%s)) - INTERVAL '1 day',
        INTERVAL '1 day'
    )::DATE AS day
),
event_counts AS (
    SELECT DATE(created_at) AS day, COUNT(*) AS count
    FROM posts
    WHERE board_name = %s
      AND created_at >= TO_TIMESTAMP(%s)
      AND created_at < TO_TIMESTAMP(%s)
      AND (
            LOWER(COALESCE(subject, '')) LIKE ANY(%s)
            OR LOWER(COALESCE(comment, '')) LIKE ANY(%s)
          )
    GROUP BY DATE(created_at)
)
SELECT ds.day, COALESCE(ec.count, 0) AS count
FROM date_series ds
LEFT JOIN event_counts ec ON ds.day = ec.day
ORDER BY ds.day;
"""

# Event-related posts timeline for 4chan - ALL boards (no community filter)
SELECT_CHAN_EVENT_RELATED_ALL = """
WITH date_series AS (
    SELECT generate_series(
        DATE(TO_TIMESTAMP(%s)),
        DATE(TO_TIMESTAMP(%s)) - INTERVAL '1 day',
        INTERVAL '1 day'
    )::DATE AS day
),
event_counts AS (
    SELECT DATE(created_at) AS day, COUNT(*) AS count
    FROM posts
    WHERE created_at >= TO_TIMESTAMP(%s)
      AND created_at < TO_TIMESTAMP(%s)
      AND (
            LOWER(COALESCE(subject, '')) LIKE ANY(%s)
            OR LOWER(COALESCE(comment, '')) LIKE ANY(%s)
          )
    GROUP BY DATE(created_at)
)
SELECT ds.day, COALESCE(ec.count, 0) AS count
FROM date_series ds
LEFT JOIN event_counts ec ON ds.day = ec.day
ORDER BY ds.day;
"""
