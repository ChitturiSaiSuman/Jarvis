import netifaces, nmap, psutil, re, subprocess

def get_local_ip_address():
    '''
    Retrieves the IP address of the machine within a router network.

    Returns:
        str or None: The IP address of the machine if found, or None if unable to retrieve the IP address.
    '''
    try:
        # Get a list of all network interfaces
        interfaces = netifaces.interfaces()

        # Find the interface that is connected to the router
        for interface in interfaces:
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses:
                ip_address = addresses[netifaces.AF_INET][0]['addr']
                if ip_address != '127.0.0.1':
                    return ip_address

    except (OSError, KeyError):
        pass

    return None


def get_connected_ssid():
    '''
    Retrieves the SSID of the Wi-Fi router the Raspberry Pi is currently connected to.

    Returns:
        str or None: The SSID of the connected Wi-Fi network, or None if not connected to any network.
    '''
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


def get_cpu_temperature():
    '''
    Retrieves the current CPU temperature of a Raspberry Pi running Ubuntu Server.

    Returns:
        float: The current CPU temperature in Celsius, or None if the temperature information is unavailable.
    '''
    try:
        temperature = psutil.sensors_temperatures()

        if 'cpu_thermal' in temperature:
            cpu_temp = temperature['cpu_thermal'][0].current
            return cpu_temp
    except:
        pass

    return None


def discover_wireless_siblings():
    '''
    Retrieves a list of devices connected to the Wi-Fi network within a specified IP range.

    Returns:
        list: A list of tuples containing device information. Each tuple consists of (device_name, device_ip).
              device_name (str): The name or hostname of the connected device.
              device_ip (str): The IP address of the connected device.

    Note:
        This function utilizes Nmap to scan the specified IP range and determine the devices that are up (online)
        on the network. It assumes that Nmap is installed and available in the system's PATH.

    Example:
        >>> discover_wireless_siblings()
        [('Device1', '192.168.1.100'), ('Device2', '192.168.1.101'), ('Device3', '192.168.1.102')]

    '''
    try:
        # Create a new Nmap Scanner
        port_scanner = nmap.PortScanner()

        # Define the target IP range of the Wi-Fi network
        target_ip_range = '192.168.1.0/24'

        # Perform the Scan
        port_scanner.scan(hosts=target_ip_range, arguments='-sn')

        devices = list()
        for host in port_scanner.all_hosts():
            if port_scanner[host].state() == 'up':
                device_name = port_scanner[host]['hostnames'][0]['name']
                device_ip = port_scanner[host]['addresses']['ipv4']
                devices.append((device_name, device_ip))

        return sorted(devices, key=lambda pair: pair[1])
    except:
        pass

    return []


if __name__ == '__main__':
    print(get_local_ip_address())
    print(get_connected_ssid())
    print(get_cpu_temperature())
    print(discover_wireless_siblings())