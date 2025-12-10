# REDDIT
SELECT_SUBREDDIT_COUNT = "SELECT count(distinct(id)) FROM subreddit"

# Engagement by Post Type (Graph 4A) - Reddit
# Joins posts with comments using post_id column
SELECT_REDDIT_ENGAGEMENT_BY_TYPE = """
SELECT 
    post_type,
    COUNT(*) AS total_threads,
    AVG(reply_count) AS avg_replies,
    SUM(reply_count) AS total_replies
FROM (
    SELECT 
        p.unique_name,
        p.title,
        p.is_video,
        COUNT(CASE WHEN c.body IS NOT NULL AND c.body != '' AND c.body != '[deleted]' AND c.body != '[removed]' THEN 1 END) AS reply_count,

        /* ------------------------------------------
           Enhanced Post-Type Classification (Matches 4chan)
           ------------------------------------------ */
        CASE 
            /* ---- Strong question detection ---- */
            WHEN LOWER(p.title) ~ '\?$'
              OR LOWER(p.title) LIKE '%%why%%'
              OR LOWER(p.title) LIKE '%%how%%'
              OR LOWER(p.title) LIKE '%%what do you think%%'
              OR LOWER(p.title) LIKE '%%is it true%%'
              OR LOWER(p.title) LIKE '%%should i%%'
            THEN 'Question'

            /* ---- Expanded news detection ---- */
            WHEN LOWER(p.title) LIKE ANY (ARRAY[
                '%%news%%', '%%breaking%%', '%%breaking news%%',
                '%%report%%', '%%reported%%', '%%update%%',
                '%%journalist%%', '%%press%%', '%%headline%%',
                '%%alert%%', '%%source:%%'
            ])
            THEN 'News'

            /* ---- Meme classification ---- */
            WHEN COALESCE(p.is_video, false) = true
              OR LOWER(p.title) LIKE ANY (ARRAY[
                    '%%meme%%','%%dank%%','%%lol%%','%%funny%%',
                    '%%cope%%','%%cringe%%','%%based%%','%%shitpost%%'
              ])
              OR LOWER(COALESCE(p.thumbnail, '')) IN ('image', 'gif')
            THEN 'Meme'

            /* ---- Opinion detection ---- */
            WHEN LOWER(p.title) LIKE ANY (ARRAY[
                '%%i think%%','%%in my opinion%%','%%imo%%',
                '%%my view%%','%%my take%%','%%i believe%%',
                '%%it seems to me%%','%%i feel like%%','%%personally%%'
            ])
            THEN 'Opinion'

            ELSE 'Opinion'
        END AS post_type

    FROM posts p
    LEFT JOIN comments c ON c.post_id = p.unique_name

    WHERE 
        p.subreddit = %s
        AND p.created_at >= %s
        AND p.created_at < %s

    GROUP BY p.unique_name, p.title, p.is_video, p.thumbnail
) t
GROUP BY post_type
ORDER BY post_type;
"""

# Get list of subreddits
SELECT_ALL_SUBREDDITS = """
SELECT unique_name, title, description, subscribers, over18
FROM subreddit
ORDER BY subscribers DESC
"""

SELECT_REDDIT_SUMMARY_STATS = """
SELECT 
    COUNT(*) AS total_posts,
    COUNT(DISTINCT subreddit) AS unique_subreddit,
    (SELECT COUNT(*) FROM toxicity) AS total_toxicity,
    (SELECT COUNT(*) FROM comments) AS total_comments
FROM posts;
"""

# Daily post counts by subreddit
SELECT_DAILY_POST_COUNTS_BY_SUBREDDIT = """
SELECT 
    DATE(created_timestamp) as date,
    subreddit as subreddit_name,
    COUNT(*) as counts
FROM posts
WHERE subreddit IN ('ArtificialInteligence', 'geopolitics', 'technology')
    {date_filter}
GROUP BY DATE(created_timestamp), subreddit
ORDER BY date, subreddit
"""

# Get Number SubScribers
SELECT_NUMBER_OF_SUBSCRIBERS = """
SELECT 
    title as subreddit_name,
    subscribers
FROM public.subreddit
ORDER BY subscribers Desc
LIMIT 10
"""


# Get Average Toxicity by Subreddit
SELECT_SUBREDDIT_TOXICITY = """
SELECT subreddit, toxicity FROM toxicity WHERE toxicity IS NOT NULL
"""

# Event-related posts timeline for Reddit
# Uses created_timestamp (TIMESTAMP) column for date filtering
# Generates complete date series to show 0 counts for days without matches
SELECT_REDDIT_EVENT_RELATED = """
WITH date_series AS (
    SELECT generate_series(
        DATE(TO_TIMESTAMP(%s)),
        DATE(TO_TIMESTAMP(%s)) - INTERVAL '1 day',
        INTERVAL '1 day'
    )::DATE AS day
),
event_counts AS (
    SELECT day, SUM(count) AS count
    FROM (
        -- Reddit posts
        SELECT DATE(created_timestamp) AS day, COUNT(*) AS count
        FROM posts
        WHERE subreddit = %s
          AND created_timestamp >= TO_TIMESTAMP(%s)
          AND created_timestamp < TO_TIMESTAMP(%s)
          AND LOWER(title) LIKE ANY(%s)
        GROUP BY DATE(created_timestamp)

        UNION ALL

        -- Reddit comments
        SELECT DATE(created_timestamp) AS day, COUNT(*) AS count
        FROM comments
        WHERE subreddit = %s
          AND created_timestamp >= TO_TIMESTAMP(%s)
          AND created_timestamp < TO_TIMESTAMP(%s)
          AND LOWER(body) LIKE ANY(%s)
        GROUP BY DATE(created_timestamp)
    ) combined
    GROUP BY day
)
SELECT ds.day, COALESCE(ec.count, 0) AS count
FROM date_series ds
LEFT JOIN event_counts ec ON ds.day = ec.day
ORDER BY ds.day;
"""

# Event-related posts timeline for Reddit - ALL subreddits (no community filter)
SELECT_REDDIT_EVENT_RELATED_ALL = """
WITH date_series AS (
    SELECT generate_series(
        DATE(TO_TIMESTAMP(%s)),
        DATE(TO_TIMESTAMP(%s)) - INTERVAL '1 day',
        INTERVAL '1 day'
    )::DATE AS day
),
event_counts AS (
    SELECT day, SUM(count) AS count
    FROM (
        -- Reddit posts (all subreddits)
        SELECT DATE(created_timestamp) AS day, COUNT(*) AS count
        FROM posts
        WHERE created_timestamp >= TO_TIMESTAMP(%s)
          AND created_timestamp < TO_TIMESTAMP(%s)
          AND LOWER(title) LIKE ANY(%s)
        GROUP BY DATE(created_timestamp)

        UNION ALL

        -- Reddit comments (all subreddits)
        SELECT DATE(created_timestamp) AS day, COUNT(*) AS count
        FROM comments
        WHERE created_timestamp >= TO_TIMESTAMP(%s)
          AND created_timestamp < TO_TIMESTAMP(%s)
          AND LOWER(body) LIKE ANY(%s)
        GROUP BY DATE(created_timestamp)
    ) combined
    GROUP BY day
)
SELECT ds.day, COALESCE(ec.count, 0) AS count
FROM date_series ds
LEFT JOIN event_counts ec ON ds.day = ec.day
ORDER BY ds.day;
"""
