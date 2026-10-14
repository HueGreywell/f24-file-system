# F24 Browser-Based File System

A small browser-based file system with folders, name-only files, recursive
deletion, global filename-prefix search, and exact-name search in the
current folder. React frontend, FastAPI backend, PostgreSQL database.

## Run everything with Docker

```bash
docker compose up --build
```

This starts PostgreSQL, applies the database migrations, then starts the
API and the frontend.

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

## Run locally (without Docker)

### Database

```bash
docker compose up -d postgres
```

### Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env   # update POSTGRES_PORT to 5433 to match the compose mapping above
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

Open http://localhost:5173.

## Tests

Unit tests (service layer, name validation, API routing/error-mapping) run
against an in-memory fake repository and need no database:

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

## API

- `GET /folders` / `GET /folders/{id}` — folder metadata, derived path, and
  immediate children.
- `POST /folders/{id}` — create a file or folder, returns `201`.
- `DELETE /folders/{id}` — recursively delete a non-root folder.
- `DELETE /files/{id}` — delete a file.
- `GET /files/search?query=x` — prefix search across all files, top 10
  matches. Add `&folderId=y` to instead require an exact (case-insensitive)
  name match scoped to that one folder. The frontend's search box exposes
  both: typing searches globally by prefix, and an "exact name, this folder
  only" checkbox switches to the scoped exact-match lookup.

Errors use `{ "code": "...", "message": "..." }`. Invalid requests return
`400`, missing resources `404`, name conflicts `409`, and unexpected
failures `500`.
