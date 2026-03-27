"""CLI entry point."""

from __future__ import annotations

import click
from rich.console import Console

from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.domain.exceptions import AuthError, CLIError
from workouter_cli.infrastructure.config.loader import ConfigError, load_config
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.presentation.context import CLIContext
from workouter_cli.presentation.middleware.error_handler import (
    handle_cli_error,
    handle_unexpected_error,
)
from workouter_cli.presentation.middleware.logging import setup_logging
from workouter_cli.utils.exit_codes import ExitCode


class SafeGroup(click.Group):
    """Click group with centralized CLI error handling."""

    def invoke(self, ctx: click.Context) -> object:
        output_json = bool(ctx.params.get("output_json", False))
        command = ctx.command_path

        try:
            return super().invoke(ctx)
        except CLIError as error:
            handle_cli_error(error, output_json=output_json, command=command)
        except click.exceptions.Exit:
            raise
        except click.ClickException:
            raise
        except Exception as error:  # pragma: no cover - defensive fallback
            handle_unexpected_error(error, output_json=output_json, command=command)


@click.group(cls=SafeGroup)
@click.option("--json", "output_json", is_flag=True, help="Output machine-readable JSON")
@click.option("--timeout", type=int, default=None, help="Override request timeout in seconds")
@click.version_option(package_name="workouter-cli")
@click.pass_context
def cli(ctx: click.Context, output_json: bool, timeout: int | None) -> None:
    """Workouter CLI."""

    if ctx.resilient_parsing:
        return

    if ctx.invoked_subcommand is None:
        return

    if ctx.invoked_subcommand == "schema":
        return

    try:
        config = load_config()
        effective_timeout = timeout if timeout is not None else config.timeout
        setup_logging(config)
        client = GraphQLClient(
            url=str(config.api_url), api_key=config.api_key, timeout=effective_timeout
        )
        ctx.obj = CLIContext(
            config=config,
            client=client,
            output_json=output_json,
            timeout=effective_timeout,
        )
    except ConfigError as error:
        code = "AUTH_ERROR" if error.exit_code == ExitCode.AUTH_ERROR else "VALIDATION_ERROR"
        handle_cli_error(
            CLIError(message=str(error), exit_code=error.exit_code, code=code),
            output_json=output_json,
            command=ctx.command_path,
        )


@cli.command(name="schema")
def schema() -> None:
    """Show command schema placeholder."""

    click.echo('{"success": true, "data": {"message": "schema command placeholder"}}')


@cli.command(name="ping")
@click.pass_obj
def ping(ctx: CLIContext) -> None:
    """Validate startup and print ready."""

    formatter = get_formatter(ctx.output_json)
    payload = {"message": "ready", "timeout": ctx.timeout}
    rendered = formatter.format(payload, command="ping")

    if isinstance(rendered, str):
        click.echo(rendered)
    else:
        Console().print(rendered)


@cli.command(name="raise-auth", hidden=True)
def raise_auth() -> None:
    """Test-only command that raises AuthError."""

    raise AuthError("Invalid API key")
