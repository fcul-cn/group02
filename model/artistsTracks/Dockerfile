FROM postgres

USER postgres
WORKDIR /app

COPY model/artistsTracks/create.sql /docker-entrypoint-initdb.d/create.sql

EXPOSE 5432
