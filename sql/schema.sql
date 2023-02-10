CREATE TABLE tokens (
    email TEXT NOT NULL UNIQUE,
    token TEXT NOT NULL UNIQUE
);

CREATE TABLE dishes (
    id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,
    imageUrl TEXT NOT NULL,
    ingredients JSON,
    timestamp TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE TABLE accounts (
    id BIGINT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    password TEXT NOT NULL,
    confirmed BOOLEAN
);

CREATE TABLE bookmarks (
    account BIGINT,
    dish BIGINT,
    timestamp TIMESTAMP DEFAULT NOW() NOT NULL,

    PRIMARY KEY (account, dish),
    CONSTRAINT FK_2 FOREIGN KEY (dish)
        REFERENCES dishes(id)
            ON DELETE CASCADE,

    CONSTRAINT FK_3 FOREIGN KEY (account)
        REFERENCES accounts(id)
            ON DELETE CASCADE
);

CREATE TABLE details (
    id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,
    readyInMinutes INT NOT NULL,
    imageUrl TEXT NOT NULL,
    ingredients JSON NOT NULL,
    instructions JSON NOT NULL,

    CONSTRAINT FK_1 FOREIGN KEY (id)
        REFERENCES dishes(id)
            ON DELETE CASCADE
);


