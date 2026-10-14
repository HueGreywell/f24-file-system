# F24 Browser-Based File System

A small browser-based file system with folders, name-only files, recursive
deletion, global filename-prefix search, and filename-prefix search scoped
to the current folder. React frontend, FastAPI backend, PostgreSQL database.

## Run everything with Docker

```bash
docker compose up --build
```

This starts PostgreSQL, applies the database migrations, then starts the
API and the frontend.

Note: `backend/migrations/0003_seed_data.sql` is demo seed data (a few
sample folders/files), not a schema change — it runs like any other
migration so the app has something to browse out of the box. To start with
an empty filesystem instead, delete that file before running migrations
for the first time.

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

Stop the stack with:

```bash
docker compose down
```

To also remove the database volume:

```bash
docker compose down -v
```

## Run locally (backend/frontend without Docker)

Tool versions used, not pinned anywhere else in the repo (library versions
are in `backend/pyproject.toml` and `frontend/package.json`/`package-lock.json`):

- Python 3.12
- Node 22
- npm 11

### Database

Install PostgreSQL yourself instead and
point `backend/.env` at it (`POSTGRES_HOST`/`POSTGRES_PORT`/`POSTGRES_DB`/
`POSTGRES_USER`/`POSTGRES_PASSWORD`).

### Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env
.venv/bin/python -m app.db.migrate
.venv/bin/uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Tests

Unit tests (service layer, name validation, API routing/error-mapping)

```bash
cd backend
.venv/bin/pytest tests --ignore=tests/integration
```

Integration tests exercise the real SQL (uniqueness constraints, cascading
delete, path building, search) against Postgres. Start the database first:

```bash
docker compose up -d postgres
cd backend
.venv/bin/pytest tests/integration
```

Running `.venv/bin/pytest` with no arguments runs both; the integration
tests are skipped automatically if no database is reachable.

## Running in debug mode

Both apps can be launched under a debugger directly from VS Code
(`.vscode/launch.json`):

- **Backend: FastAPI (uvicorn)** — runs the API with `debugpy` attached, so
  breakpoints in `backend/app` are hit. Requires the Python extension with
  the `backend/.venv` interpreter selected, and PostgreSQL running (see
  above).
- **Frontend: Launch Chrome** — starts the Vite dev server and opens it in
  a debuggable Chrome instance, so breakpoints in `frontend/src` are hit
  directly in `.tsx`/`.ts` source.
- **Debug: Backend + Frontend** — runs both at once.

Any other IDE works the same way: point it at `backend/.venv` for Python
debugging, and use its browser/JS debugger (or just browser DevTools, which
work out of the box against the Vite dev server's source maps) for the
frontend.
