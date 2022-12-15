CREATE TABLE IF NOT EXISTS recipes (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    original_name TEXT NOT NULL,
    readyInMinutes INT NOT NULL,
    imageUrl TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
)

CREATE TABLE IF NOT EXISTS recipe_details (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    original_name TEXT NOT NULL,
    readyInMinutes INT NOT NULL,
    imageUrl TEXT NOT NULL,
    ingredients JSON NOT NULL,
    instructions JSON NOT NULL,
    last_looked TIMESTAMP DEFAULT NOW() NOT NULL
)

CREATE TABLE IF NOT EXISTS accounts (
    id VARCHAR(12) PRIMARY KEY,
    email TEXT NOT NULL,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confirmed BOOLEAN NOT NULL DEFAULT 0
)

CREATE TABLE IF NOT EXISTS bookmarks (
    recipe_id BIGINT NOT NULL,
    account_id BIGINT NOT NULL,

    PRIMARY KEY (recipe_id, account_id)
)
