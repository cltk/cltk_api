#!/bin/bash

NAME="CLTK API"
SOCKFILE=/home/cltk/cltk_api/binding.sock 
NUM_WORKERS=4

echo "Starting $NAME"

#activate virtual environment
source /home/cltk/venv/bin/activate
cd /home/cltk/cltk_api
	
# Start gunicorn server
exec gunicorn api_json:app -b 127.0.0.1:5000 \
  --workers $NUM_WORKERS \
  --bind=unix:$SOCKFILE
