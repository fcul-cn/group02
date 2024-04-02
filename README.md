# fcul-cn-group2 - Instructions for the building and deployment

# 1. Make sure you have Docker and Git installed on your machine

If you don´t you can access to both check these link for documentation: 
- https://www.docker.com/get-started/
- https://git-scm.com/downloads

# 2. Setup environment variables in our local machine

The necessary environment variables and values are the following:
- POSTGRES_USER: The name of user the databases of your choice.
- POSTGRES_DB: The name of the databases of your choice. 
- POSTGRES_PASSWORD: The password of the databases of your choice.
- POSTGRES_PORT: 5432
- POSTGRES_ARTIST_HOST: 172.100.10.7
- POSTGRES_ARTIST_RELEASE_HOST: 172.100.10.18
- POSTGRES_GENRE_HOST: 172.100.10.10
- POSTGRES_PLAYLIST_HOST: 172.100.10.13
- POSTGRES_RELEASE_HOST: 172.100.10.16
- POSTGRES_TRACK_HOST: 172.100.10.4

# 3. Clone the project

Clone the project to your machine using the command:

```git clone https://github.com/fcul-cn/group02.git```

# 4. Build and Run

To run the full application, at the root of the project, execute the command:

```docker-compose up -d ```

# 5. Test the APIs

At the folder /docs of the project, there is a JSON file that can be imported to the Postman application to make requests to the APIs endpoints. You can also consult the APIs' specification in the file openapi-group2.yaml located at the same folder.