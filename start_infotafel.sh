#!/bin/bash

set -e

# Simple setup script for a freshly installed Ubuntu system.
# Installs dependencies, sets up a virtual environment and starts
# the Django development server.

# Ensure required system packages are present
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip

# Create virtual environment if not already done
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment and install Python dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations and start the server
cd infotafel_project
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
