# Install pip
    sudo apt install python3-pip

# Install system utilities
    sudo apt install nmap wireless-tools

# Install Transmission Daemon, a BitTorrent client
    sudo apt-get install transmission-daemon

# Stop Transmission Daemon to edit configuration
    sudo service transmission-daemon stop

# Edit the Transmission Daemon configuration file
    sudo sed -i 's/"rpc-whitelist-enabled": true,/"rpc-whitelist-enabled": false,/' /etc/transmission-daemon/settings.json

# Restart Transmission Daemon
    sudo service transmission-daemon start

# Install Python packages
    sudo pip3 install -r requirements.txt