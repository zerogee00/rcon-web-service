#!/bin/bash

# Install Python dependencies
pip3 install -r requirements.txt

# Copy systemd service file
sudo cp rcon-web.service /etc/systemd/system/

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable rcon-web.service

echo "Setup complete! To start the service:"
echo "sudo systemctl start rcon-web.service"
echo ""
echo "Remember to:"
echo "1. Set your API_TOKEN in /etc/systemd/system/rcon-web.service"
echo "2. Set your SLACK_SIGNING_SECRET in /etc/systemd/system/rcon-web.service"
echo "3. Configure your Cloudflare tunnel to point to localhost:5000"
