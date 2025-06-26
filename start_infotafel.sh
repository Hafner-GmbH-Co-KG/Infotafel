#!/bin/bash

set -e

# Simple setup script for a freshly installed Ubuntu system.
# Installs dependencies, ensures the project files are up to date,
# sets up a virtual environment and starts the Django development
# server.

# URL of the GitHub repository to clone if the project is not yet
# present locally. Adjust this to your own repository if needed.
REPO_URL="https://github.com/example/Infotafel.git"

# If the script is not running inside a git working tree, clone the
# repository to a new directory and continue from there.
if [ ! -d .git ]; then
    git clone "$REPO_URL" Infotafel
    cd Infotafel
fi

# When already inside a git repository, fetch the latest changes.
git pull --ff-only

# Ensure required system packages are present
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip

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
