# Preparation

Define the follow environment keys

- POSTGRES_ARTIST_HOST: 172.100.10.7
- POSTGRES_ARTISTS_RELEASES_HOST: 172.100.10.18
- POSTGRES_GENRE_HOST: 172.100.10.10
- POSTGRES_RELEASE_HOST: 172.100.10.16
- POSTGRES_PLAYLIST_HOST: 172.100.10.13
- POSTGRES_TRACK_HOST: 172.100.10.4
- POSTGRES_DB: < DB_NAME >
- POSTGRES_PASSWORD: < PASSWORD >
- POSTGRES_HOST: < PORT >
- POSTGRES_USER: < USER >

# Building

1. For building the application you must have the docker installed.
2. Open the terminal and go to the root page of the project.
3. Then use the follow command:

```
docker-compose up
```

# How to use

We recommend the use of postman to test the application. In this phase you have to change the ports to a specific type of requests. For example, the tracks are exposed in port 5000 an the artists are in port 5001. Use the swagger to see the possible routes.
