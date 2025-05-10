
import click

import utils
from commands import table_cmd
from commands import links_cmd
import subprocess
import sys
import os
#You also need to have nmap.exe installed on the system and it also needs to be in the system path directory
# pip install python-nmap
import nmap

@click.group()
def spoof():
    """

    """
    pass


@spoof.command()
def start():
    """
    Start the spoofing session. While in the session, you
    will still be able to use the terminal as you would normally do.
    """
    gui_script = os.path.join(os.path.dirname(__file__), "session.py")

    if sys.platform.startswith("win"):
        # Windows: use 'start' to detach
        subprocess.Popen(["start", "python", gui_script], shell=True)
    else:
        # macOS/Linux
        subprocess.Popen(
            [sys.executable, gui_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

    utils.print_info_message("Spoofing session successfully started.")

#ip_mask in this case is something like this '192.168.0.0/24' which specifies which part of the local network to explore the standard ones are
#192.168.1.0/24 and 192.168.0.0/24 but it depends on the network observe computers local ip to get a guess.
#this function returns a list of ip adress that contain the devices in the local network.
#type of device
def probe_network(ip_mask):

    # Initialize the nmap.PortScanner object
    nm = nmap.PortScanner()

    # Define the local network range
    network_range = ip_mask   # Scanning the entire mask

    # Scan the network for hosts that are up with additional options
    nm.scan(hosts=network_range, arguments='-sn')  # Ping scan**

    # Print all discovered hosts and their details
    print("Devices found in the network:")
    for host in nm.all_hosts():
        if nm[host].state() == 'up':  # Check if the host is up
            # Try to detect the device type
            device_type = nm[host].hostname()
            if not device_type:
                device_type = "Unknown"  # If no hostname, mark as unknown
            print(f"IP Address: {host}")
                    # Try to get MAC address and vendor
            if 'mac' in nm[host]['addresses']:
                mac = nm[host]['addresses']['mac']
                vendor = nm[host]['vendor'].get(mac, 'Unknown')
                print(f"MAC Address: {mac} + Interface Vendor ({vendor})")
            else:
                print("MAC Address: Unknown")

spoof.add_command(table_cmd.dns_spoof_table)
spoof.add_command(links_cmd.target_links)
