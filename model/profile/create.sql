BEGIN TRANSACTION;

CREATE TABLE User(
    user_id BIGINT PRIMARY KEY NOT NULL,
    email TEXT UNIQUE NOT NULL,
    user_name TEXT UNIQUE NOT NULL
);

CREATE TABLE Playlist(
    playlist_id BIGINT PRIMARY KEY NOT NULL,
    user_id BIGINT NOT NULL,
    playlist_name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Track(
    track_id BIGINT PRIMARY KEY NOT NULL
);

CREATE TABLE PlaylistTrack(
    playlist_id BIGINT NOT NULL,
    track_id BIGINT NOT NULL,
    date_added DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (playlist_id) REFERENCES Playlist(playlist_id),
    FOREIGN KEY (track_id) REFERENCES Track(track_id),
    PRIMARY KEY (playlist_id, track_id)
);

COMMIT;