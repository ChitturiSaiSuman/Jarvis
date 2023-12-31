import src.services.informio
from src.common import response
from src.services import librarian
from src.flows import Librarian_Flows

# informer = src.services.informio.Informio()

# resp = response.Response('info', 'Info Response')

# informer.send_message(resp.to_string())

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


# obj = librarian.Librarian()
# zip_file = obj.archive_creator('app.py', 'hello')

# print(obj.tome_transporter(zip_file))

locator = Librarian_Flows.FileLocator()

files = locator.exec({
    'path': "/home/suman/Music",
    'pattern': "mp3",
    "domain": "title"
}).get('response')

print(*enumerate(files), sep = '\n')

index = int(input('pick a file:'))

uploader = Librarian_Flows.FileUploader()

resp = uploader.exec({
    "path": files[index],
    # "compress": True,
    # "password": "ass"
})

print(resp['response'])