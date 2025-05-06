import click
import table_cmd
from spoof_session import SpoofSession

@click.group()
def spoof():
    pass


@spoof.command()
@click.argument("address", type=str)
def start(address):
    """ Start the spoof. """
    SpoofSession(address)

spoof.add_command(table_cmd.table)
