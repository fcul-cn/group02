BEGIN TRANSACTION;

CREATE TABLE Tracks(
    track_id SERIAL PRIMARY KEY NOT NULL,
    title TEXT UNIQUE NOT NULL,
    mix TEXT UNIQUE NOT NULL,
    is_remixed BOOLEAN NOT NULL,
    release_date DATE NOT NULL,
    genre_id BIGINT NOT NULL,
    subgenre_id BIGINT NOT NULL,
    track_url TEXT UNIQUE NOT NULL,
    bpm INTEGER NOT NULL,
    duration INTEGER NOT NULL
);

COMMIT;