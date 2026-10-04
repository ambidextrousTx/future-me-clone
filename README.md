# future-me-clone
A clone of FutureMe.org for local hosting

## Tech stack
* Python (Asyncpg, Asyncio, Pydantic, FastAPI)
* Postgres
* ?? for frontend

## Running tests (once the cluster is up)
```bash
$ docker compose exec backend pytest
```

## Monorepo structure
```
future-me-clone/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   └── ...
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py          # FastAPI app entrypoint
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── db.py            # DB connection/session setup
│   │   ├── scheduler.py     # APScheduler job(s)
│   │   ├── email_sender.py  # the swappable send-email interface
│   │   └── routes/
│   │       └── emails.py
│   └── tests/
│
├── db/
│   ├── init.sql             # optional: seed schema on first container start
│   └── migrations/          # if we add Alembic later
│
└── docs/
    └── architecture.md      # notes like the ones we're generating now
```
