import click

import utils
from commands import table_cmd
from commands import links_cmd
import subprocess
import sys
import os

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


spoof.add_command(table_cmd.dns_spoof_table)
spoof.add_command(links_cmd.target_links)
