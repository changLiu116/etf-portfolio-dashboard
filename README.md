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

## Stage 2: DynamoDB holdings

The holdings API stores manually maintained ETF information in DynamoDB.
`quantity`, `average_cost`, and `account` are optional. If omitted, those
attributes are not written to DynamoDB and are not returned in API responses.

### AWS configuration

The backend uses boto3's standard AWS credential chain. Configure credentials
outside this repository, for example through the AWS CLI or AWS IAM Identity
Center. Never place access keys in source code or commit them to Git.

The application configuration defaults are:

```text
AWS_REGION=ca-central-1
DYNAMODB_TABLE_NAME=etf-portfolio-dashboard-dev
PORTFOLIO_ID=default
```

Each value can be overridden with an environment variable. After AWS
authentication is configured, create the on-demand development table from the
`backend/` directory:

```bash
python scripts/create_dynamodb_table.py
```

The script is safe to run more than once: it leaves an existing table alone.

### Holdings endpoints

With the API running, the following routes are available:

```text
POST   /holdings
GET    /holdings
GET    /holdings/{holding_id}
PUT    /holdings/{holding_id}
DELETE /holdings/{holding_id}
```

Example request body without private position information:

```json
{
  "ticker": "XGRO",
  "exchange": "TSX",
  "currency": "CAD",
  "average_cost": "27.42"
}
```

The latest market quote is intentionally not stored on a holding. It will be
retrieved from a market-data provider in Stage 3 so the API can report its
source, observation time, currency, and whether it is delayed.
