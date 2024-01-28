# FYI (Since you'd come back again after long time
# and totally forget if the following worked):
    # The following code is Working perfectly fine

import subprocess

def run_bluetoothctl_command(command):
    # Spawn bluetoothctl process
    proc = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Send the command to bluetoothctl
    proc.stdin.write(command + '\n')
    proc.stdin.flush()

    # Read the output
    output = proc.communicate()[0]

    # Close the process
    proc.stdin.close()
    proc.stdout.close()
    proc.stderr.close()

    return output

# Example usage:
result = run_bluetoothctl_command('connect B8:16:5F:B1:90:3E')
# result = run_bluetoothctl_command('devices')
# result = run_bluetoothctl_command('remove B8:16:5F:B1:90:3E')

print(result)
