git fetch && git pull
source .venv/Scripts/activate
gunicorn -w 4 -b 0.0.0.0 'main:app'