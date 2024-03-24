FROM postgres

USER postgres
WORKDIR /app

COPY model/track/create.sql /docker-entrypoint-initdb.d/create.sql

EXPOSE 5432
