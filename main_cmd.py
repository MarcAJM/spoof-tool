import click
import table_cmd
from spoof_session import SpoofSession

@click.group()
def spoof():
    pass

@spoof.command()
def start():
    """ Start the spoof. """
    SpoofSession("192.156.533.245")

spoof.add_command(table_cmd.table)
