import click

def print_error_message(message):
    click.echo(click.style("✖ ", bold=True, fg="red") + click.style(message, bold=True))

def print_info_message(message):
    click.echo(click.style("ℹ ", bold=True, fg="blue") + click.style(message, bold=True))