# Week 2: Action Item Extractor

## Overview

This project is a minimal FastAPI + SQLite app that turns free-form meeting notes into actionable tasks.

It supports two extraction modes:
- **Heuristic extraction** using rule-based parsing for bullets, checkboxes, and action prefixes.
- **LLM extraction** using Ollama with structured JSON output (`action_items: string[]`), plus retry/fallback behavior.

The app also includes a simple HTML frontend to:
- paste notes,
- run extraction (`Extract` / `Extract LLM`),
- mark action items complete,
- list saved notes.

## Project Structure

- `app/main.py` - FastAPI app setup, router registration, and frontend serving.
- `app/routers/action_items.py` - action item endpoints (extract/list/mark done).
- `app/routers/notes.py` - note endpoints (create/list/get by id).
- `app/services/extract.py` - heuristic + LLM extraction logic.
- `app/db.py` - SQLite schema and CRUD operations.
- `frontend/index.html` - lightweight UI for extraction and notes listing.
- `tests/test_extract.py` - unit/integration-style tests for extraction logic.
- `tests/run_tests.py` - test runner that configures import path correctly.

## Setup and Run

### 1) Install dependencies

From the repository root (`modern-software-dev-assignments`):

```bash
poetry install
```

If you use Conda, activate your environment first, then run `poetry install`.

### 2) (Optional) Configure environment variables

- `OLLAMA_MODEL` (default: `llama3.2-vision`)
- `APP_TZ_OFFSET_HOURS` (default: `8`, China Standard Time / UTC+8)

Example:

```bash
set OLLAMA_MODEL=llama3.2-vision
set APP_TZ_OFFSET_HOURS=8
```

### 3) Start Ollama (required for LLM extraction)

Make sure Ollama is running and the model is available:

```bash
ollama run llama3.2-vision
```

### 4) Run the API server

From the repository root:

```bash
poetry run uvicorn week2.app.main:app --reload
```

Open:
- App UI: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

## API Endpoints

### Root / Frontend

- `GET /`
  - Returns the frontend page (`frontend/index.html`).

### Notes

- `POST /notes`
  - Create a note.
  - Body:
    ```json
    { "content": "Meeting notes..." }
    ```
  - Returns: created note (`id`, `content`, `created_at`).

- `GET /notes`
  - List all notes (newest first).

- `GET /notes/{note_id}`
  - Get one note by id.
  - Returns `404` if not found.

### Action Items

- `POST /action-items/extract`
  - Heuristic extraction from `text`.
  - Body:
    ```json
    { "text": "notes...", "save_note": true }
    ```
  - Returns: `note_id` (if saved) and extracted `items`.

- `POST /action-items/extract-llm`
  - LLM extraction via Ollama with structured output.
  - Same body/response shape as `/action-items/extract`.
  - Includes retry and fallback to heuristic extraction when Ollama is unavailable.

- `GET /action-items`
  - List all action items.
  - Optional query param: `note_id` to filter by note.

- `POST /action-items/{action_item_id}/done`
  - Mark an action item done/undone.
  - Body:
    ```json
    { "done": true }
    ```

## Frontend Functionality

The UI provides:
- **Extract** button -> calls `/action-items/extract`
- **Extract LLM** button -> calls `/action-items/extract-llm`
- **List Notes** button -> calls `/notes`
- Checkbox toggles -> call `/action-items/{id}/done`

## Running Tests

Run the provided test runner from the repository root:

```bash
python week2/tests/run_tests.py
```

This runner ensures imports resolve correctly for the `week2` package.

You can also run pytest directly from the repository root:

```bash
python -m pytest week2/tests/test_extract.py -v --tb=short
```

### Test Notes

- `tests/test_extract.py` includes:
  - rule-based extraction tests,
  - real Ollama-backed LLM tests (no mock),
  - a 3-second delay between LLM tests to reduce back-to-back call failures.
- For stable LLM test execution, keep Ollama running before starting tests.

