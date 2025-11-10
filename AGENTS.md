# Repository Guidelines

## Project Structure & Module Organization
- `backend/` hosts the FastAPI service (`main.py`) plus SQLAlchemy models, Pydantic schemas, and CRUD helpers; keep new DB logic near `crud.py`.
- `frontend/` is a lightweight Vue 3 single-page app (`index.html`, `app.js`, `styles.css`). Add UI assets beside these files and keep the build step-free.
- `data/` is created at runtime for SQLite; never commit its contents. Deployment files (`Dockerfile`, `docker-compose.yml`, `OPENMEDIAVAULT_DEPLOYMENT.md`) live in the repo root.

## Build, Test, and Development Commands
- `docker-compose up -d --build` — Rebuilds backend image and starts the stack on port 8000.
- `docker-compose logs -f backend` — Streams backend logs for live debugging.
- `cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000` — Runs the API locally without Docker.
- `cd frontend && python -m http.server 8080` — Serves the static frontend for local iteration.

## Coding Style & Naming Conventions
- Python uses 4-space indentation, type hints, and FastAPI async endpoints; keep names snake_case (`get_recent_matches`) and raise HTTPException for errors.
- Vue logic in `app.js` should keep camelCase data/computed keys and kebab-case props in templates.
- Format Python via `python -m black backend` and `isort backend`; keep CSS selectors mobile-first and scoped by view IDs.

## Testing Guidelines
- Add pytest coverage in `backend/tests/` (create as needed) for CRUD helpers and response schemas; seed temp SQLite DBs via fixtures.
- Name tests `test_<feature>_<scenario>` and cover both happy paths and constraint failures.
- Run `pytest backend/tests -q` before raising a PR; share coverage notes when touching persistence layers.

## Commit & Pull Request Guidelines
- Use short, imperative subjects (“Add OpenMediaVault deployment support”) under ~70 characters and describe user-visible impact in the body.
- Reference issues when applicable (`Refs #12`) and note any schema or API adjustments.
- PRs should outline the change, list manual test commands+results, and include screenshots/GIFs for UI work; flag Compose or Docker changes explicitly.

## Security & Configuration Tips
- Keep secrets in Compose overrides or environment variables; never commit `.env` files or contents of `data/`.
- Validate payloads via Pydantic before writes and sanitize frontend-bound strings to avoid HTML injection.
