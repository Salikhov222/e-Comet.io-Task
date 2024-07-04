#!/bin/bash

set -u

function create_database() {
    local database=$1
    echo "Creating database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
EOSQL

    # Connect to the newly created database and create tables
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$database" <<-EOSQL
        CREATE TABLE top_repos (
            id SERIAL PRIMARY KEY,
            repo TEXT NOT NULL,
            owner TEXT NOT NULL,
            position_cur INT,
            position_prev INT,
            stars INT NOT NULL,
            watchers INT NOT NULL,
            forks INT NOT NULL,
            open_issues INT NOT NULL,
            language TEXT
        );

        CREATE TABLE IF NOT EXISTS repo_activity (
            id SERIAL PRIMARY KEY,
            repo_id INTEGER REFERENCES top_repos(id) NOT NULL,
            date DATE NOT NULL,
            commits INTEGER NOT NULL,
            authors TEXT[] NOT NULL,
            CONSTRAINT repo_date_unique UNIQUE (repo_id, date)
        );

EOSQL
}

if [ -n "$POSTGRES_DB_NAME" ]; then
    echo "Database creation requested: $POSTGRES_DB_NAME"
    create_database "$POSTGRES_DB_NAME"
    echo "Database with tables created"
fi
