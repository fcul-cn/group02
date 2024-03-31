FROM postgres

USER postgres
WORKDIR /app

COPY model/playlist/create.sql /docker-entrypoint-initdb.d/create.sql

EXPOSE 5432