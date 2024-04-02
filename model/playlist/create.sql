BEGIN TRANSACTION;

CREATE TABLE Playlist(
    playlist_id SERIAL PRIMARY KEY NOT NULL,
    user_id BIGINT NOT NULL,
    playlist_name TEXT NOT NULL,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE PlaylistTrack(
    playlist_id BIGINT NOT NULL,
    track_id BIGINT NOT NULL,
    date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (playlist_id) REFERENCES Playlist(playlist_id),
    PRIMARY KEY (playlist_id, track_id)
);

COMMIT;