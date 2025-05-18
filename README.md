# nask_task

## Setup

1. Install dependencies:
```bash
poetry install
```
2. Copy envs:
```bash
cp .env.sample .env
```
3. Install pre-commit hooks:
```bash
pre-commit install
```

4. Run the application:
```bash
docker compose up
```

## Usage

- **Create a task:**
  - `POST /task` (optionally with `callback_url`)
  - Returns: `{ "task_id": "<id>" }`

- **Check task status:**
  - `GET /task/{task_id}`
  - Returns Server-Sent Events (SSE) with task status updates.
