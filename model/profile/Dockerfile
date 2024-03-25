FROM postgres

USER postgres
WORKDIR /app

COPY model/profile/create.sql /docker-entrypoint-initdb.d/create.sql

EXPOSE 5432