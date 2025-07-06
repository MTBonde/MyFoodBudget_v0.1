#!/bin/bash
python db_init.py
exec flask run --host=0.0.0.0 --port=5000
