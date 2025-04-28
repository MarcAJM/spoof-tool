import click
import dns_spoof_table
import style
from tabulate import tabulate

@click.group()
def table():
    pass

@table.command()
@click.argument("domainname", type=str)
@click.argument("ip_address", type=str)
def add(domainname, ip_address):
    style.print_success_message("Added table entry (" + domainname + ", " + ip_address + ")")
    dns_spoof_table.add(domainname, ip_address)

@table.command()
@click.argument("domainname", type=str)
def remove(domainname):
    ip_address = dns_spoof_table.get(domainname)
    style.print_success_message("Removed table entry (" + domainname + ", " + ip_address + ")")
    dns_spoof_table.remove(domainname)

@table.command()
def show():
    print(tabulate(list(dns_spoof_table.get_rows()), headers=["Domain", "IP Address"], tablefmt="fancy_outline"))
