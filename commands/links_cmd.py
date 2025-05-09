import click
from tabulate import tabulate
import utils
from tables import target_links_table as table

@click.group()
def target_links():
    """
    A target link is a link from one IP address to another.
    This command contains several subcommands to add, remove, or show
    the target links. When a link is added, the attacker (you) will be in
    the middle of this link. You will receive all the information that passes
    this link.
    """
    pass


@target_links.command()
@click.argument('ip1', type=str)
@click.argument('ip2', type=str)
def add(ip1, ip2):
    """ Adds a target link to the table. """
    utils.print_info_message("Added link (" + ip1 + ", " + ip2 + ")")
    table.add(ip1, ip2)


@target_links.command()
@click.argument('ip1', type=str)
@click.argument('ip2', type=str)
def remove(ip1, ip2):
    """ Removes a specific target link from the table. """
    utils.print_info_message("Removed link (" + ip1 + ", " + ip2 + ")")
    table.remove(ip1, ip2)


@target_links.command()
def remove_all():
    """ Removes all the target links from the table. """
    utils.print_info_message("Removed all links")
    table.remove_all()


@target_links.command()
def show():
    """ Prints out all the target links. """
    rows = [[f'({link[0]}, {link[1]})'] for link in table.get_all()]
    print(tabulate(rows, tablefmt="double_grid"))