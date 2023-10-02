import subprocess
import re

def get_connected_ssid():
    try:
        output = subprocess.check_output(["iwconfig", "wlan0"])
        output = output.decode()

        # Use regular expressions to extract the SSID from the output
        match = re.search(r'ESSID:"([^"]+)"', output)
        if match:
            return match.group(1)
    except subprocess.CalledProcessError:
        pass

    return None

ssid = get_connected_ssid()
if ssid:
    print("Connected SSID:", ssid)
else:
    print("Not connected to any Wi-Fi network.")
