# DetectNet

DetectNet is a final-year project prototype for multilingual cyberbullying detection. It combines:

- Rule-based NLP for transparent abusive pattern detection
- A transformer-ready ML scoring layer for contextual risk estimation
- FastAPI for backend APIs
- Streamlit for the frontend dashboard and live analysis workflow

## Project Structure

- `backend/` - API, schemas, and analysis services
- `frontend/` - Streamlit app
- `storage/` - Local evidence and report logs created at runtime

## Run Locally

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the FastAPI backend:

```powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

3. Start the Streamlit frontend in another terminal:

```powershell
python -m streamlit run frontend/streamlit_app.py --server.address 127.0.0.1 --server.port 8501

### Windows quick launch

To keep both services alive in separate windows on Windows, run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\launch_detectnet.ps1
```

Or start them individually:

```powershell
.\start_backend.ps1
.\start_frontend.ps1
```
```

## Demo URLs

- Streamlit: `http://127.0.0.1:8501`
- FastAPI docs: `http://127.0.0.1:8000/docs`

## Streamlit Community Cloud Deployment

This repository is deployment-ready for Streamlit Community Cloud.

- Recommended entrypoint: `streamlit_app.py`
- Branch: `main`
- Python version: `3.12` on Streamlit Cloud
- No `secrets.toml` is required for the standalone demo

### Deployment modes

1. `Standalone Streamlit Cloud mode`

- The app directly imports the backend analysis modules.
- This is the easiest option for public deployment.
- You only deploy the Streamlit app.

2. `External API mode`

- Set `API_URL` in Streamlit secrets or environment variables.
- The frontend will call a hosted FastAPI backend instead of local modules.

### Community Cloud steps

1. Open Streamlit Community Cloud and click `Create app`.
2. Select this GitHub repository and the `main` branch.
3. Set the entrypoint file to `streamlit_app.py`.
4. Choose Python `3.12` in Advanced settings.
5. Deploy the app.
