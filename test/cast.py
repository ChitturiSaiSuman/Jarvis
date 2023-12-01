from scapy.all import ARP, Ether, srp

# Define your local IP address and subnet mask
local_ip = "192.168.1.1/24"  # Replace this with your local subnet
arp = ARP(pdst=local_ip)

# Create an Ethernet frame with the ARP packet
ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast Ethernet frame

# Combine the Ethernet frame and ARP packet
packet = ether/arp

# Send the packet and receive a list of answered devices
result = srp(packet, timeout=3, verbose=0)[0]

# Extract and print the IP and MAC addresses of discovered devices
devices = []
for sent, received in result:
    devices.append({'ip': received.psrc, 'mac': received.hwsrc})

print("List of Smart Devices on the Network:")
for device in devices:
    print(f"IP Address: {device['ip']}, MAC Address: {device['mac']}")
