#!/usr/bin/python3

import datetime
import logging
import os
import re
import subprocess
import traceback
from io import TextIOWrapper

import netifaces
import nmap
import psutil

from src.common.config import Constants

class UTIL:

    @staticmethod
    def get_local_time() -> dict:
        '''
        Get the current local time and return it as a formatted string.
    
        This method retrieves the current local time using the `datetime` module,
        formats it according to the '%c' format string, and returns the formatted
        time as a string.

        Returns:
            str: A string representing the current local time in a human-readable format.

        Example:
            >>> local_time = MyClass.get_local_time()
            >>> print(local_time)
            'Mon Sep 29 15:48:03 2023'
        '''
        try:
            local_time = datetime.datetime.now().strftime('%c')
            return {
                'status': 'success',
                'message': local_time
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': traceback.format_exc()
            }

    @staticmethod
    def get_current_working_directory():
        '''
        Get the current working directory as a string.

        This method returns the absolute pathname of the current working directory
        of the process. The current working directory is the directory in which
        the Python script is currently executing.

        Returns:
            str: A string representing the absolute path of the current working directory.

        Example:
            >>> cwd = MyClass.get_current_working_directory()
            >>> print(cwd)
            '/path/to/current/directory'        
        '''
        try:
            return {
                'status': 'success',
                'message': os.getcwd()
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': traceback.format_exc()
            }
    

    @staticmethod
    def get_local_ip_address():
        '''
        Retrieves the IP address of the machine within a router network.

        Returns:
            str or None: The IP address of the machine if found, or None if unable to retrieve the IP address.
        '''
        try:
            ip = None
            # Get a list of all network interfaces
            interfaces = netifaces.interfaces()

            # Find the interface that is connected to the router
            for interface in interfaces:
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses:
                    ip_address = addresses[netifaces.AF_INET][0]['addr']
                    if ip_address != '127.0.0.1':
                        ip = ip_address
                        break

            return {
                'status': 'success',
                'message': ip
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': traceback.format_exc()
            }
    
    @staticmethod
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
                ssid = match.group(1)

            return {
                'status': 'success',
                'message': ssid
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': traceback.format_exc()
            }
    
    @staticmethod
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
                
            return {
                'status': 'success',
                'message': cpu_temp
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': traceback.format_exc()
            }
    
    @staticmethod
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

            return {
                'status': 'success',
                'message': '\n'.join([f'{device}: {ip}' for device, ip in sorted(devices, key=lambda pair: pair[1])])
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': traceback.format_exc()
            }
        
    @staticmethod
    def get_log(N=10) -> str:
        '''
        Retrieves the last N lines from the Jarvis application log file.

        This method reads the Jarvis application log file, which is managed by the Python logging module,
        and retrieves the last N lines. The log file contains information about system events, errors,
        and other diagnostic messages logged during the operation of the Jarvis application.

        Returns:
            str: A string containing the last N lines from the Jarvis application log file.

        Note:
            The log file is assumed to be managed by the Python logging module. The specific location and
            format of the log file may be configured in the application's logging setup.
        '''
        try:
            log_file = TextIOWrapper(open(Constants['log']))
            return {
                'status': 'success',
                'message': log_file.readlines()[-N:]
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': traceback.format_exc()
            }
    
    @staticmethod
    def reboot():
        '''
        Reboots the system.

        Returns:
            bool: True if the restart command was successful, False otherwise.
        '''
        try:
            subprocess.run(["sudo", "reboot"])
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def shutdown():
        '''
        Shuts down the system.

        Returns:
            bool: True if the shutdown command was successful, False otherwise.
        '''
        try:
            subprocess.run(["sudo", "shutdown", "-h", "now"])
            return True
        except subprocess.CalledProcessError:
            return False


if __name__ == '__main__':
    print(UTIL.get_local_ip_address())
    print(UTIL.get_connected_ssid())
    print(UTIL.get_cpu_temperature())
    print(UTIL.discover_wireless_siblings())