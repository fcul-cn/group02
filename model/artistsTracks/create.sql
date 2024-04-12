create table ArtistsTracks(
    artist_id int not null,
    track_id int not null,
    primary key (artist_id, track_id),
);