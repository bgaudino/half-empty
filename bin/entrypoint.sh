#!/bin/bash

set -m # to make job control work
supercronic crontab &
gunicorn --bind :8000 --workers 2 half_empty.wsgi &
fg %1 # gross!
