DROP TABLE IF EXISTS replies CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE IF NOT EXISTS "users" (
    auth0_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category_followed TEXT[]
);

CREATE TABLE IF NOT EXISTS "posts" (
    pid SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    upvotes INTEGER DEFAULT 0,
    image: TEXT NULL,
    downvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author_name VARCHAR(255) NOT NULL,
    category TEXT NOT NULL,
    deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (author_name) REFERENCES "users" (username) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "replies" (
    cid SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author_name TEXT NOT NULL,
    post_id INTEGER NOT NULL,
    deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (author_name) REFERENCES "users" (username) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES "posts" (pid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "votes" (
    vid SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    post_id INTEGER,
    reply_id INTEGER,
    vote_type VARCHAR(10) NOT NULL CHECK (vote_type IN ('upvote', 'downvote')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, post_id),
    UNIQUE(user_id, reply_id),
    FOREIGN KEY (user_id) REFERENCES "users" (auth0_id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES "posts" (pid) ON DELETE CASCADE,
    FOREIGN KEY (reply_id) REFERENCES "replies" (cid) ON DELETE CASCADE
);
