#!/bin/bash
# Script to start the FastAPI backend server
# Run this from the project root directory

echo "Starting ATS Scanner Backend Server..."
echo "Make sure you're in the project root directory!"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found!"
    echo "Please create a .env file with your MongoDB URI and other configuration."
    echo ""
fi

# Start the server
uvicorn backend.backend_api:app --reload --port 8000

