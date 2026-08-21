# Flow Forge API

Dify-aligned Workflow learning backend (Flask + Pydantic + SQLite).

## Setup

```bash
cd api
uv sync
```

## Tests

```bash
cd api
uv run pytest
```

## Run

```bash
cd api
uv run flask --app flow_forge.app:create_app run --debug
```

Then open `http://127.0.0.1:5000/health`.
