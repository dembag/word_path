# Local PostgreSQL database

The app uses PostgreSQL for local development when `DATABASE_URL` points to a PostgreSQL server. Install PostgreSQL 16 or newer using the installer or package manager for your operating system, then start its database service.

Create a database and user for the project using your local PostgreSQL administration tool. For example, in `psql`:

```sql
CREATE USER word_path WITH PASSWORD 'change-me';
CREATE DATABASE word_path OWNER word_path;
```

Copy `.env.example` to `.env` if needed, then set `DATABASE_URL` to match the local server credentials:

```text
DATABASE_URL=postgresql+psycopg://word_path:change-me@localhost:5432/word_path
```

Start the FastAPI app as described in [learner-interface.md](learner-interface.md). The app creates its tables during startup and seeds the built-in symbol catalog.

To remove the local database, use your PostgreSQL administration tool to drop the `word_path` database. This permanently deletes its data.
