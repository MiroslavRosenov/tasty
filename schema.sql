CREATE TABLE IF NOT EXISTS dishes (
    id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,
    imageUrl TEXT NOT NULL,
    ingredients JSON,
    timestamp TIMESTAMP DEFAULT NOW() NOT NULL
)

CREATE TABLE IF NOT EXISTS details (
    id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,
    readyInMinutes INT NOT NULL,
    imageUrl TEXT NOT NULL,
    ingredients JSON NOT NULL,
    instructions JSON NOT NULL
)

CREATE TABLE IF NOT EXISTS bookmarks (
    account BIGINT NOT NULL,
    dish BIGINT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW() NOT NULL
    UNIQUE (account, dish)
)

CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL,
    email TEXT NOT NULL UNIQUE,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    password TEXT NOT NULL,
    confirmed BOOLEAN
)

CREATE TABLE IF NOT EXISTS tokens (
    token TEXT NOT NULL,
    email TEXT NOT NULL,
    UNIQUE (token, email)
)