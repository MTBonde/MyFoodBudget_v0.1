#!/bin/bash

echo "Initializing DB if needed..."
python db_init.py

echo "Starting app..."
exec python app.py
