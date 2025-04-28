import click
import table_cmd

@click.group()
def spoof():
    pass

@spoof.command()
def start():
    click.echo("TODO")

spoof.add_command(table_cmd.table)
