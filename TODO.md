# TODO

- [x] Add PUT/PATCH/DELETE endpoints and CRUD helpers for players, games, and matches to allow correcting or removing records.
- [ ] Validate duplicates gracefully by checking for existing player/game names (or catching `IntegrityError`) and returning HTTP 409.
- [ ] Optimize `/api/stats` by aggregating counts in SQL rather than looping per player/game.
- [ ] Introduce pytest coverage under `backend/tests/` for CRUD operations and stats calculations, including constraint failures.
- [ ] Add basic authentication or token checks and tighten CORS defaults before exposing the API beyond the LAN.
- [ ] Serve frontend assets through a small reverse proxy or add caching headers so static files are cached by browsers.
