# Workout Plan Generator

A Streamlit + FastAPI app that generates a personalized workout plan using Groq's LLM.

## Architecture

- **`frontend/`** — Streamlit UI. Collects goal/experience/equipment/days/injuries, calls the backend over HTTP, renders the response.
- **`backend/`** — FastAPI service. Validates the request, builds the LLM prompt, calls Groq, validates the response, returns structured JSON.

The two only communicate over the `/generate-plan` REST endpoint — Streamlit never calls Groq directly.

## Setup

1. Install [`uv`](https://docs.astral.sh/uv/) if you don't have it.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Create a `.env` file in the project root with your Groq credentials:
   ```
   GROQ_API_KEY=your-groq-api-key-here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```
   Get an API key at [console.groq.com](https://console.groq.com). Check [console.groq.com/docs/models](https://console.groq.com/docs/models) for current available model names.

## Running the app

You need both the backend and frontend running at the same time, in **two separate terminals**.

**Terminal 1 — backend:**
```bash
uv run uvicorn backend.main:app --reload
```
Runs at `http://localhost:8000`. Visit `http://localhost:8000/docs` for an interactive API explorer.

**Terminal 2 — frontend:**
```bash
uv run streamlit run frontend/app.py
```
Opens at `http://localhost:8501`.

## Running tests

```bash
uv run pytest backend/tests/ -v
```
