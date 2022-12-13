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
    ingredients JSON,
    instructions JSON
)