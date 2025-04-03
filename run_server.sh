#!/bin/bash

# Terminate any existing servers
pkill -f runserver
pkill -f daphne
pkill -f process_tasks

# Run Django development server for static files
python3 manage.py runserver 8000 &

# Wait a moment for the Django server to start
sleep 2
# Run Daphne for WebSockets on a different port
daphne -p 8001 core.asgi:application &


echo "Servers started:"
echo "Django development server running on http://127.0.0.1:8000"
echo "Daphne ASGI server running on http://127.0.0.1:8001"
echo "5 task processor workers running in background"
echo "Press Ctrl+C to stop all servers"

# Run 5 task processor workers without limit
python3 manage.py process_tasks --continuous --sleep 30 --limit 10


# Wait for user to press Ctrl+C
wait
