# Backend Structure

This backend is built with FastAPI.

## Directory Structure

- `app/`: Main application code.
  - `main.py`: Entry point of the application.
  - `api/`: API route definitions.
    - `v1/endpoints/`: Specific API endpoints (e.g., agents).
  - `core/`: Core configuration and settings.
  - `agents/`: Logic for your agents (move your agent code here).
  - `tools/`: Tools used by agents (move your tool code here).
- `requirements.txt`: Python dependencies.

## Running the App

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
