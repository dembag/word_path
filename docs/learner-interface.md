# Run the learner interface locally

The learner interface is served by the FastAPI app; no separate frontend server or build step is needed.

## Start the app

From the project directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Configure `.env` in the project directory. For the local PostgreSQL setup, follow [local-database.md](local-database.md) and set `DATABASE_URL` as described there. Set `OPENAI_API_KEY` and `OPENAI_MODEL` to enable question generation. The app can start without an OpenAI key, but it cannot create a new practice session.

Start FastAPI:

```powershell
uvicorn main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in Chrome. The first page lists the profiles already in the database. FastAPI creates the database tables and seeds the built-in symbol catalog at startup; it does not create a learner profile or assign vocabulary automatically.

## Prepare a learner profile

If the profile page is empty, open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and:

1. Use `POST /users` to create a profile. Include a name, age band, `starting_format` (`choice` or `sentence`), at least one `communication_goals` entry, and the desired prompt display and card size.
2. Use `GET /symbols` to find symbol IDs.
3. Add symbols with `POST /vocabulary/{user_id}`, supplying `symbol_id` and `page` as query parameters. Repeat for each symbol the learner should have.

The seed ingestion script can populate the symbol catalog and image files before assigning vocabulary. Run it from the project root with the database configured:

```powershell
python scripts/ingest_seed_symbols.py
```

## Use the interface

1. On the profile splash, select a learner.
2. Choose an enabled communication goal and start the practice session. The practice format is taken from the saved profile.
3. On each question, use **Hear again** to replay it. In choice mode, only the question's available symbols can be selected; other vocabulary remains visible but dimmed. Choice cues play at 10 and 20 seconds. In sentence mode, build a response from the vocabulary board and submit it.
4. Use **Next** to leave a question unanswered or advance after answering. On the final question, use **Finish** to complete the session and view the results, unanswered questions, and any generated review.
5. Return to profiles to select another learner. Profile settings are available before a session starts.

If question generation is unavailable, check that the app process can read the configured OpenAI key and model, then review the server log. The learner interface itself is served locally and can still be opened without a key.
