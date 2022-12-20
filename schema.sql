CREATE TABLE IF NOT EXISTS dishes (
    id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,
    imageUrl TEXT NOT NULL,
    ingredients JSON,
    timestamp TIMESTAMP
)

CREATE TABLE IF NOT EXISTS details (
    id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,
    readyInMinutes INT NOT NULL,
    imageUrl TEXT NOT NULL,
    ingredients JSON NOT NULL,
    instructions JSON NOT NULL,
)

CREATE TABLE IF NOT EXISTS bookmarks (
    recipe_id BIGINT NOT NULL,
    account_id BIGINT NOT NULL,

    PRIMARY KEY (recipe_id, account_id)
)

CREATE TABLE IF NOT EXISTS accounts (
    id VARCHAR(12) PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confirmed BOOLEAN
)

CREATE TABLE IF NOT EXISTS tokens (
    token TEXT NOT NULL,
    email TEXT NOT NULL,
    UNIQUE (token, email)
)