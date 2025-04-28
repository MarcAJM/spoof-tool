import click

def print_success_message(message):
    click.echo(click.style("✓ ", bold=True, fg="green") + message)

def print_error_message(message):
    click.echo(click.style("☓ ", bold=True, fg="red") + message)

def print_info_message(message):
    click.echo(click.style("➤", bold=True, fg="blue") + message)