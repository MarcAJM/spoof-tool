import scapy
import click

@click.group()
def spoof():
    pass

@spoof.command()
def start():
    click.echo("TODO")

@spoof.group()
def dns_spoof_table():
    pass

@dns_spoof_table.command()
def add(domainname: str, ip_address: str):
    click.echo("TODO")

@dns_spoof_table.command()
def remove(domainname: str):
    click.echo("TODO")

