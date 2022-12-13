CREATE TABLE IF NOT EXISTS recipes (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    readyInMinutes INT NOT NULL,
    image TEXT NOT NULL,
    sourceUrl TEXT
)

CREATE TABLE IF NOT EXISTS recipe_details (
    
)