FROM postgres

USER postgres
WORKDIR /app

COPY model/artist/create.sql /docker-entrypoint-initdb.d/create.sql

EXPOSE 5432
