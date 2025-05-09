import click
from tables import dns_spoof_table as table
import utils
from tabulate import tabulate


@click.group()
def dns_spoof_table():
    """ Represents the DNS spoofing table. """
    pass


@dns_spoof_table.command()
@click.argument("domainname", type=str)
@click.argument("ip_address", type=str)
def add(domainname, ip_address):
    """ Add a new <domainname, ip_address> pair to the table. """
    utils.print_info_message("Added table entry (" + domainname + ", " + ip_address + ")")
    table.add(domainname, ip_address)


@dns_spoof_table.command()
@click.argument("domainname", type=str)
def remove(domainname):
    """ Remove table entry with <domainname>."""
    ip_address = table.get(domainname)
    if ip_address is None:
        utils.print_error_message("Table entry does not exist")
    else:
        utils.print_info_message("Removed table entry (" + domainname + ", " + ip_address + ")")
        table.remove(domainname)


@dns_spoof_table.command()
def remove_all():
    """ Remove all entries from the table."""
    table.remove_all()
    utils.print_info_message("Removed all table entries")


@dns_spoof_table.command()
def show():
    """ Outputs the dns spoofing table in a nice manner. """
    print(tabulate(list(table.get_rows()), headers=["Domainname", "Malicious IP Address"], tablefmt="fancy_outline"))
