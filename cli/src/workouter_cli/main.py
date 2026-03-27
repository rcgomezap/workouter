"""CLI entry point."""

import click

from workouter_cli.infrastructure.config.loader import ConfigError, load_config
from workouter_cli.presentation.middleware.logging import setup_logging


@click.group()
@click.version_option(package_name="workouter-cli")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Workouter CLI."""

    if ctx.resilient_parsing:
        return

    if ctx.invoked_subcommand is None:
        return

    if ctx.invoked_subcommand == "schema":
        return

    try:
        config = load_config()
        setup_logging(config)
        ctx.obj = {"config": config}
    except ConfigError as error:
        click.echo(f"Error: {error}", err=True)
        raise click.exceptions.Exit(error.exit_code.value) from error


@cli.command(name="schema")
def schema() -> None:
    """Show command schema placeholder."""

    click.echo('{"success": true, "data": {"message": "schema command placeholder"}}')


@cli.command(name="ping")
@click.pass_context
def ping(ctx: click.Context) -> None:
    """Validate startup and print ready."""

    _ = ctx.obj["config"]
    click.echo("ready")
