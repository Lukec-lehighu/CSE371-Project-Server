git fetch && git pull
source .venv/Scripts/activate
gunicorn -w 4 'main:app'