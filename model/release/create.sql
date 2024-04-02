BEGIN TRANSACTION;

CREATE TABLE Releases(
    release_id SERIAL PRIMARY KEY NOT NULL,
    release_title TEXT UNIQUE NOT NULL,
    release_date DATE NOT NULL,
    release_url TEXT UNIQUE NOT NULL,
    updated_on DATE NOT NULL
);

COMMIT;