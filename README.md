# ETF Portfolio Dashboard

A learning project for building an ETF portfolio dashboard with a React
frontend and a Python/FastAPI backend. The project is being developed in small
stages; currently, only the Stage 1 backend foundation is present.

## Stage 1: local Python API

### Prerequisites

- Python 3.12

The repository pins the backend to Python 3.12 in `backend/.python-version`.
Check your installed version with:

```bash
python3.12 --version
```

### Set up the backend

From the repository root:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The virtual environment is local to `backend/` and is intentionally excluded
from Git. Run `deactivate` when you want to leave it.

If `.venv` has already been created in this workspace, activate it directly:

```bash
cd backend
source .venv/bin/activate
```

### Run the API

With the virtual environment active and from the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

The local endpoints are:

- API: <http://127.0.0.1:8000>
- Health check: <http://127.0.0.1:8000/health>
- Interactive API documentation: <http://127.0.0.1:8000/docs>
- OpenAPI document: <http://127.0.0.1:8000/openapi.json>

The health endpoint should return:

```json
{"status": "ok"}
```

### Run the tests

With the virtual environment active and from the `backend/` directory:

```bash
pytest
```
