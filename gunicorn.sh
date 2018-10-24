#! /bin/bash

gunicorn -D -b unix:./gun_buyrabbit.sock -w 4 -p ./gun_buyrabbit.pid buyrabbit.wsgi