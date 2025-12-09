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
    CASE 
        WHEN COALESCE(comment, '') ILIKE '%%?%%' THEN 'question'
        WHEN COALESCE(comment, '') ILIKE '%%news%%' OR COALESCE(comment, '') ILIKE '%%breaking%%' THEN 'news'
        WHEN filename IS NOT NULL AND ext IN ('.jpg', '.png', '.gif') THEN 'meme'
        ELSE 'opinion'
    END as post_type,
    COUNT(DISTINCT post_no) as total_threads,
    AVG(replies) as avg_replies,
    AVG(images) as avg_images,
    SUM(replies) as total_replies
FROM posts
WHERE board_name = %s
    AND resto = 0
    AND to_timestamp(post_time) >= %s::timestamp
    AND to_timestamp(post_time) < (%s::timestamp + interval '1 day')
GROUP BY post_type
ORDER BY post_type
"""