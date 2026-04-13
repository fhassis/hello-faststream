# Define base image
FROM docker.io/python:3.14-slim-trixie

# Avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install PostgreSQL 18 Client from PGDG repository
RUN apt-get update && apt-get install -y lsb-release wget gnupg \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/postgresql-archive-keyring.gpg] http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y postgresql-client-18 \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=dialog
