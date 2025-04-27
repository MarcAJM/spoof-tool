import click
import dns_spoof_table

@click.group()
def spoof():
    pass

@spoof.command()
def start():
    click.echo("TODO")

@spoof.group()
def table():
    pass

@table.command()
@click.argument("domainname", type=str)
@click.argument("ip_address", type=str)
def add(domainname, ip_address):
    dns_spoof_table.add(domainname, ip_address)

@table.command()
@click.argument("domainname", type=str)
def remove(domainname):
    dns_spoof_table.remove(domainname)

@table.command()
def remove_all():
    dns_spoof_table.remove_all()

