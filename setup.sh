# Install pip
sudo apt install python3-pip

# Install system utilities
sudo apt install nmap wireless-tools

# Install Python packages
sudo pip3 install python-nmap psutil discord.py discord_webhook google-auth google-api-python-client pyzipper

# Install Transmission Daemon, a BitTorrent client
sudo apt-get install transmission-daemon
sudo pip3 install transmission-rpc

# Stop Transmission Daemon to edit configuration
sudo service transmission-daemon stop

# Edit the Transmission Daemon configuration file
sudo sed -i 's/"rpc-whitelist-enabled": true,/"rpc-whitelist-enabled": false,/' /etc/transmission-daemon/settings.json

# Restart Transmission Daemon
sudo service transmission-daemon start
