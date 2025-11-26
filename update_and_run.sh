git fetch && git pull
source .venv/bin/activate
gunicorn -w 4 -b 0.0.0.0 'main:app'