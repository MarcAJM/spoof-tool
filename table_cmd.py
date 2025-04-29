import click
import dns_spoof_table
import utils
from tabulate import tabulate

@click.group()
def table():
    """ Represents the DNS spoofing table. """
    pass

@table.command()
@click.argument("domainname", type=str)
@click.argument("ip_address", type=str)
def add(domainname, ip_address):
    """ Add a new <domainname, ip_address> pair to the table. """
    utils.print_info_message("Added table entry (" + domainname + ", " + ip_address + ")")
    dns_spoof_table.add(domainname, ip_address)

@table.command()
@click.argument("domainname", type=str)
def remove(domainname):
    """ Remove table entry with <domainname>."""
    ip_address = dns_spoof_table.get(domainname)
    utils.print_info_message("Removed table entry (" + domainname + ", " + ip_address + ")")
    dns_spoof_table.remove(domainname)

@table.command()
def remove_all():
    """ Remove all entries from the table."""
    dns_spoof_table.remove_all()
    utils.print_info_message("Removed all table entries")

@table.command()
def show():
    """ Outputs the dns spoofing table in a nice manner. """
    print(tabulate(list(dns_spoof_table.get_rows()), headers=["Domainname", "Malicious IP Address"], tablefmt="fancy_outline"))
