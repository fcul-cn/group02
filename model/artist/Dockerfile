FROM postgres

USER postgres
WORKDIR /app

COPY model/artist/create.sql /docker-entrypoint-initdb.d/artist.sql

EXPOSE 5432