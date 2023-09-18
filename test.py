import src.services.informio
from src.common import response

informer = src.services.informio.Informio()

resp = response.Response('info', 'Info Response')

informer.send_message(resp.to_string())

#!/usr/bin/python3
# import os

# s = """
# # This file is generated from information provided by the datasource.  Changes
# # to it will not persist across an instance reboot.  To disable cloud-init's
# # network configuration capabilities, write a file
# # /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg with the following:
# # network: {config: disabled}
# network:
#     version: 2
#     wifis:
#         renderer: networkd
#         wlan0:
#             access-points:
#                 "<SSID>":
#                     password: "<PASSWORD>"
#             dhcp4: true
#             optional: true
# """

# s = s.replace("<SSID>", ssid)
# s = s.replace("<PASSWORD>", password)


# with open('/etc/netplan/50-cloud-init.yaml', 'w') as file:
# 	file.write(s)

# os.system('sudo netplan apply')


