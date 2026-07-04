#!/bin/bash

# iWater Bot Setup Script
# Developed for Ubuntu/Debian

echo "--- iWater Bot Setup System ---"

# 1. Update System
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# 2. Check Python 3.12
echo "Checking Python 3.12..."
if ! command -v python3.12 &> /dev/null
then
    echo "Python 3.12 not found. Installing..."
    sudo apt install software-properties-common -y
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install python3.12 python3.12-venv python3.12-dev -y
else
    echo "Python 3.12 is already installed."
fi

# 3. Create Virtual Environment
echo "Creating virtual environment..."
python3.12 -m venv .venv
source .venv/bin/activate

# 4. Install Requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Handle .env
if [ ! -f .env ]; then
    echo ".env file not found. Let's create it."
    read -p "Enter BOT_TOKEN: " BOT_TOKEN
    read -p "Enter SUPER_ADMIN_ID (The owner ID): " SUPER_ADMIN_ID
    read -p "Enter your DOMAIN (e.g. iwater.uz): " DOMAIN
    
    echo "BOT_TOKEN=\"$BOT_TOKEN\"" > .env
    echo "SUPER_ADMIN_ID=\"$SUPER_ADMIN_ID\"" >> .env
    echo "DOMAIN=\"$DOMAIN\"" >> .env
    echo ".env file created successfully."
else
    echo ".env file already exists."
    # Check if DOMAIN exists in .env
    if ! grep -q "DOMAIN=" .env; then
        read -p "Enter your DOMAIN (e.g. iwater.uz): " DOMAIN
        echo "DOMAIN=\"$DOMAIN\"" >> .env
    fi
fi

# Load DOMAIN from .env
export $(grep -v '^#' .env | xargs)

# 6. Install Caddy
echo "Installing Caddy Server..."
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy -y

# 7. Configure Caddy
echo "Configuring Caddyfile..."
CADDY_CONF="$DOMAIN {
    reverse_proxy localhost:3001
    encode gzip
    log {
        output file /var/log/caddy/access.log
    }
}"
echo "$CADDY_CONF" | sudo tee /etc/caddy/Caddyfile
sudo systemctl restart caddy

# 8. Create systemd services
echo "Creating systemd services..."
USER_NAME=$(whoami)
PROJECT_DIR=$(pwd)

# Bot Service
SERVICE_FILE="[Unit]
Description=iWater Delivery Telegram Bot
After=network.target

[Service]
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/.venv/bin/python $PROJECT_DIR/main.py
Restart=always

[Install]
WantedBy=multi-user.target"

echo "$SERVICE_FILE" | sudo tee /etc/systemd/system/iwater_bot.service

# Web Service (FastAPI)
WEB_SERVICE_FILE="[Unit]
Description=iWater Web Landing Page (FastAPI)
After=network.target

[Service]
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/.venv/bin/uvicorn web.main:app --host 127.0.0.1 --port 3001
Restart=always

[Install]
WantedBy=multi-user.target"

echo "$WEB_SERVICE_FILE" | sudo tee /etc/systemd/system/iwater_web.service

# 9. Start services
echo "Starting and enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable iwater_bot
sudo systemctl start iwater_bot
sudo systemctl enable iwater_web
sudo systemctl start iwater_web

echo "--- Setup Complete! ---"
echo "Bot status: sudo systemctl status iwater_bot"
echo "Web status: sudo systemctl status iwater_web"
echo "Caddy status: sudo systemctl status caddy"
echo "Your site should be live at: https://$DOMAIN"
