import click
from importlib.metadata import version as get_version, PackageNotFoundError

@click.group()
def cli():
    pass

@cli.command(name="version")
def version_cmd():
    """Prints the version of the application."""
    try:
        ver = get_version("ralf")
        click.echo(f"{ver}")
    except PackageNotFoundError:
        click.echo("Package not found")

if __name__ == "__main__":
    cli()
