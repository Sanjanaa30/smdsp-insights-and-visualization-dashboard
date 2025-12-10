# REDDIT
SELECT_SUBREDDIT_COUNT = "SELECT count(distinct(id)) FROM subreddit"

# Engagement by Post Type (Graph 4A) - Reddit
SELECT_REDDIT_ENGAGEMENT_BY_TYPE = """
WITH post_comments AS (
    SELECT 
        p.unique_name,
        p.title,
        CASE 
            WHEN COALESCE(p.title, '') ILIKE '%%?%%' THEN 'question'
            WHEN COALESCE(p.title, '') ILIKE '%%news%%' OR COALESCE(p.title, '') ILIKE '%%breaking%%' THEN 'news'
            WHEN p.is_video = true OR (p.post_details->>'is_gallery')::boolean = true THEN 'meme'
            ELSE 'opinion'
        END as post_type,
        COUNT(c.comment_id) as reply_count
    FROM posts p
    LEFT JOIN comments c ON p.unique_name = c.post_id
    WHERE p.subreddit = %s
        AND p.created_at >= %s
        AND p.created_at < %s
    GROUP BY p.unique_name, p.title, p.is_video, p.post_details
)
SELECT 
    post_type,
    COUNT(*) as total_threads,
    AVG(reply_count) as avg_replies,
    SUM(reply_count) as total_replies
FROM post_comments
GROUP BY post_type
ORDER BY post_type
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
