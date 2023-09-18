import psutil
import time
import os

def get_network_usage():
    net_stats = psutil.net_io_counters(pernic=True)
    return net_stats

def format_speed(speed_bytes):
    if speed_bytes < 1024:
        return f"{speed_bytes:.2f} B/s"
    elif speed_bytes < 1024**2:
        return f"{speed_bytes / 1024:.2f} KB/s"
    elif speed_bytes < 1024**3:
        return f"{speed_bytes / (1024**2):.2f} MB/s"
    else:
        return f"{speed_bytes / (1024**3):.2f} GB/s"

def main():
    print("Monitoring network speed. Press Ctrl+C to stop.")
    try:
        prev_stats = get_network_usage()
        while True:
            curr_stats = get_network_usage()

            for interface, prev in prev_stats.items():
                curr = curr_stats.get(interface)
                if curr:
                    sent_speed = curr.bytes_sent - prev.bytes_sent
                    received_speed = curr.bytes_recv - prev.bytes_recv

                    print(f"Interface: {interface}")
                    print(f"  Sent: {format_speed(sent_speed)}")
                    print(f"  Received: {format_speed(received_speed)}")
                    print("-" * 30)

            prev_stats = curr_stats
            time.sleep(1)
            os.system('clear')
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    main()
