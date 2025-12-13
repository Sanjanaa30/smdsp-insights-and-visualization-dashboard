DB_SCHEMA = """
================== 4CHAN DATABASE (4chan_crawler) ==================
This Contains the post, for which toxicity has been scored 
TABLE toxicity (
    board_name TEXT,
    titleOrComment TEXT,
    post_no BIGINT,
    comment TEXT,
    scored_at TIMESTAMPTZ,
    language TEXT,
    toxicity REAL,
    severe_toxicity REAL,
    identity_attack REAL,
    insult REAL,
    threat REAL,
    profanity REAL,
    sexually_explicit REAL,
    flirtation REAL,
    obscene REAL,
    spam REAL,
    unsubstantial REAL,
    PRIMARY KEY (board_name, post_no)
);

TABLE posts (
    board_name TEXT,
    post_no BIGINT,
    name TEXT,
    subject TEXT,
    comment TEXT,
    filename TEXT,
    ext TEXT,
    post_time BIGINT,
    resto BIGINT,
    country TEXT,
    country_name TEXT,
    replies INT,
    images INT,
    archived BOOLEAN,
    bumplimit BOOLEAN,
    archived_on BIGINT,
    created_at TIMESTAMP
);

TABLE boards (
    board_code TEXT PRIMARY KEY,
    board_title TEXT,
    meta_description TEXT,
    ws_board INT,
    created_at TIMESTAMP
);

================== REDDIT DATABASE (reddit_crawler) ==================

TABLE posts (
    unique_name TEXT,
    author_fullname TEXT,
    author TEXT,
    title TEXT,
    subreddit TEXT,
    hidden BOOLEAN,
    thumbnail TEXT,
    over_18 BOOLEAN,
    edited BOOLEAN,
    created_at BIGINT,
    id TEXT,
    is_video BOOLEAN,
    post_details JSONB,
    created_timestamp TIMESTAMP
);
This Contains the post, for which toxicity has been scored
TABLE toxicity (
    unique_name TEXT,
    titleOrComment TEXT,
    subreddit TEXT,
    comment TEXT,
    scored_at TIMESTAMPTZ,
    language TEXT,
    toxicity REAL,
    severe_toxicity REAL,
    identity_attack REAL,
    insult REAL,
    threat REAL,
    profanity REAL,
    sexually_explicit REAL,
    flirtation REAL,
    obscene REAL,
    spam REAL,
    unsubstantial REAL,
    PRIMARY KEY (subreddit, unique_name)
);

TABLE subreddit (
    id SERIAL PRIMARY KEY,
    unique_name TEXT UNIQUE,
    title TEXT,
    subscribers INT,
    description TEXT,
    lang VARCHAR(10),
    url TEXT UNIQUE,
    created_utc DOUBLE PRECISION,
    icon_img TEXT,
    over18 BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE
);

TABLE comments (
    comment_id TEXT,
    subreddit_id TEXT,
    subreddit TEXT,
    author TEXT,
    parent_id TEXT,
    over_18 BOOLEAN,
    body TEXT,
    post_id TEXT,
    created_utc BIGINT,
    link_id TEXT,
    comment_details JSONB,
    created_timestamp TIMESTAMP
);
"""
