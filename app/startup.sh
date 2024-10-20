cd /rero/

# Activate the environemnt
. ./venv/bin/activate

# Start the app
uvicorn app.main:app --host 0.0.0.0 --port 8080
