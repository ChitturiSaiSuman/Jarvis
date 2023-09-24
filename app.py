#!/usr/bin/python3
import datetime
import logging
import os
import time

import src.common.util
import src.flows.Pirate_Flows
import src.services.informio
from src.common import config, response
from src.common.Flow import Flow

logging.basicConfig(
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO,
    filename='log.out',
    filemode='w'
)

def send_welcome(vars: dict):
    ip_address = src.common.util.UTIL.get_local_ip_address()
    wifi_ssid = src.common.util.UTIL.get_connected_ssid()
    temperature = src.common.util.UTIL.get_cpu_temperature()
    local_time = datetime.datetime.now().strftime('%c')
    devices_on_network = '\n'.join([f'{device}: {ip}' for device, ip in src.common.util.UTIL.discover_wireless_siblings()])

    message = '\n'.join([
        'Hi, Suman!',
        'This is Jarvis.',
        '',
        'For you:',
        f'Local Time: {local_time}',
        f'Network SSID: {wifi_ssid}',
        f'IP Address: {ip_address}',
        f'CPU Temperature: {temperature}',
        f'Devices on Network: \n{devices_on_network}',
        f'Current Working Directory: {os.getcwd()}'
    ])

    resp = response.Response('general', message)
    vars['informer'].send_message(resp.to_string())

def init():
    vars = {
        'informer': src.services.informio.Informio()
    }
    flows = Flow.discover_descendants()
    flows = [(flow.trigger(), flow) for flow in flows]
    return vars, flows

if __name__ == '__main__':
    time.sleep(15)
    vars, flows = init()
    logging.info(f'Found flows:')
    for flow in flows:
        logging.info(flow)
    # print(src.flows.Pirate_Flows.MagnetDownload.whoami())
    send_welcome(vars)
    import discord_bot
    token = config.Constants.creds['jarvis']['bot']['token']
    discord_bot.client.run(token)
    print("Something")
