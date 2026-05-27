# AGENTS.md

Instructions for AI coding agents working on **jojoee**.

## Project overview

jojoee is a Python project with two responsibilities:

1. **README generator** — `event.py` prints commit-time statistics to stdout; CI redirects that output to `README.md`.
2. **API server** — FastAPI app in `app/main.py` serves UTC clock images and GIFs (`module/image.py`).

Human-facing sample output is in [README.md](README.md). Do not duplicate the generated stats table here.

```
module/commit.py  →  event.py  →  README.md (via CI)
app/main.py       →  module/image.py  →  precompute/
```

## Setup

- **Python**: 3.14.5 (pinned in `.python-version`; matches CI workflows)
- **Tooling**: [uv](https://docs.astral.sh/uv/)

```bash
# Install uv: https://docs.astral.sh/uv/getting-started/installation/
uv python install 3.14.5
uv venv --python 3.14.5
source .venv/bin/activate
uv pip install -r requirements.txt -r requirements-dev.txt
```

If `.venv` has broken interpreter paths, recreate it:

```bash
rm -rf .venv
uv venv --python 3.14.5
source .venv/bin/activate
uv pip install -r requirements.txt -r requirements-dev.txt
```

**Stack**: FastAPI, uvicorn, Pillow, imageio, requests-cache, pytest, flake8.

## Commands

Run from the repository root after activating `.venv`.

| Task | Command |
|------|---------|
| Syntax check | `python3 -m py_compile module/commit.py module/image.py event.py` |
| Lint | `python -m flake8 --ignore=E501` |
| Unit tests | `python -m pytest tests/` |
| README (dry run, no API) | `python3 event.py --dryrun` |
| README (live, needs tokens) | `python3 event.py` |
| API dev server | `uvicorn app.main:app --reload --port 8000` |
| Docker build | `docker build -t jojoee .` |
| Docker run | `docker run -p 8000:8000 jojoee` |

Live README generation requires `GH_USER` and `GH_TOKEN` in the environment.

## Project structure

```
jojoee/
├── app/main.py              # FastAPI routes and scheduled cleanup
├── module/
│   ├── commit.py            # GitHub commit analysis, README table text
│   └── image.py             # PNG/GIF generation and cache paths
├── tests/test_*.py          # pytest (class-based)
├── precompute/              # Generated image/GIF cache (do not hand-edit)
│   ├── image/
│   └── gif/
├── event.py                 # README generator entry point
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
└── .github/workflows/       # CI and daily README bot
```

## Code style

- Type hints on parameters and return types.
- Import `Dict`, `List` from `typing`.
- Secrets via `os.environ.get()`, never hardcode:

```python
GITHUB_TOKEN = os.environ.get("GH_TOKEN")
```

- Docstrings with `:param` and `:return`.
- Module constants in `UPPER_CASE`.
- Safe dict access: `event.get("type")`, not `event["type"]`.
- Validate API JSON before iterating:

```python
if not isinstance(events, list):
    sys.exit(1)
```

- GitHub Compare API URLs with f-strings:

```python
f"https://api.github.com/repos/{repo}/compare/{sha1}...{sha2}"
```

**FastAPI**

- Routes: `@app.get("/path")`
- Binary responses: `StreamingResponse` with `BytesIO`
- Background cleanup: `@repeat_every` on startup handlers

## README generation (`event.py`)

`event.py` calls `show_commit_text()` from `module/commit.py` only.

CI (`.github/workflows/readme.yml`) runs `python event.py > README.md`. Changes to README content belong in `module/commit.py` and/or `event.py`, not manual edits to `README.md`.

Removing only the README footer does **not** imply removing `/api/utcnow*` endpoints in `app/main.py`.

## Exit codes

Used by `event.py` / `module/commit.py` for CI behavior:

| Exit | Meaning |
|------|---------|
| `sys.exit(1)` | Hard failure — CI must not commit |
| `sys.exit(0)` | Graceful skip — CI must not commit |
| Normal return | Success — CI may commit |

## GitHub API

- Validate response types before loops (`isinstance(..., list)`).
- Use **Compare API** for commit details; Events API omits the `commits` array.
- Rate limit: `time.sleep(0.2)` between calls.
- Auth: `requests.get(url, auth=(GITHUB_USER, GITHUB_TOKEN))`.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check `{"Hello": "World"}` |
| GET | `/api/utcnow`, `/api/utcnowimage` | UTC time as PNG |
| GET | `/api/utcnowgif` | UTC time as animated GIF |

Image routes use `is_image_request()` so non-image clients get an empty 200 instead of binary data.

## Testing

- Framework: **pytest**
- Layout: `tests/test_*.py`, class `TestRunner`, methods `test_<description>`
- CI runs: `python -m pytest tests --cov=./ --cov-report=xml`
- Add or update tests when behavior changes; skip trivial assertions.

## CI/CD

**Push** (`.github/workflows/continuous-integration.yml`): flake8 + pytest on Python 3.14.5 via uv.

**Daily README** (`.github/workflows/readme.yml`): cron `0 1 * * *` (1am UTC) runs `python event.py > README.md`, then auto-commits with `ci(bot): update README.md`.

Secrets used in workflows: `GH_USER`, `GH_TOKEN`, `GITHUB_TOKEN`. The readme workflow also references trading API env vars (`API_KEY*`, etc.) — never log or commit these.

## Git and PR conventions

- Commit messages: `feat:`, `fix:`, `docs:`, `ci(bot):`, etc.
- **Do not create git commits** unless the user explicitly asks.
- **Do not push** unless the user explicitly asks.

## Boundaries

- **Never** commit, print, or paste secrets (`.env`, `GH_TOKEN`, `API_KEY*`, `API_SECRET*`, etc.).
- **Do not** hand-edit `README.md` for the stats table — change `module/commit.py` or `event.py`.
- **Treat `precompute/`** as generated cache; avoid committing large binaries unless intentional.
- **Do not** remove UTC API endpoints when the task is only about README footer text.
- **Do not** modify `.github/workflows/readme.yml` secret names or unrelated trading env blocks without explicit request.

## Verification checklist

Before finishing a change:

1. `python3 -m py_compile module/commit.py module/image.py event.py`
2. `python3 event.py --dryrun`
3. `python -m flake8 --ignore=E501`
4. `python -m pytest tests/`
5. For API changes: `uvicorn app.main:app --reload --port 8000` and hit affected routes

Optional for README logic with credentials: `python3 event.py` (live GitHub API).

## After implementing a feature

1. Add or update tests in `tests/` when behavior changes.
2. Run lint and pytest.
3. Use conventional commit prefixes when the user requests a commit.
