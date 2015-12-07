#!/bin/bash

NAME="CLTK API"
echo "Starting $NAME"

source /home/cltk/venv/bin/activate
chdir /home/cltk/cltk_api
gunicorn -w 4 -b 0.0.0.0:5000 api_json:app
