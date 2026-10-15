# Local PostgreSQL database

The development database runs PostgreSQL 16 with the pgvector extension in Docker.

## Start

1. Start Docker Desktop and wait until its engine is running.
2. Copy `.env.example` to `.env` if you have not already done so. Set `DATABASE_URL` to the same username, password, port, and database configured for Compose. The defaults are:

   ```text
   DATABASE_URL=postgresql+psycopg://word_path:change-me@localhost:5432/word_path
   ```

3. From the project directory, start the database:

   ```powershell
   docker compose up -d db
   ```

4. Wait until it reports `healthy`:

   ```powershell
   docker compose ps
   ```

The first startup creates the `vector` extension and a named volume for database files. Changing the initialization SQL later does not rerun it for an existing volume.

## Stop and reset

Stop the container and keep the database files:

```powershell
docker compose down
```

To erase the local database and start fresh, remove its volume too:

```powershell
docker compose down -v
```

The second command permanently deletes this project's local database contents.
