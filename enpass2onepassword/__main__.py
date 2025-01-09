#!/usr/bin/env python3
import asyncio

import click

from enpass2onepassword.migration import migrate


# noinspection PyUnusedLocal
def is_positive(ctx, param, value):
    if value > 0 and isinstance(value, int):
        return value

    raise click.BadParameter("It must be a positive integer greater than zero")


# noinspection PyUnusedLocal
def is_zero_or_positive(ctx, param, value):
    if value >= 0 and isinstance(value, int):
        return value

    raise click.BadParameter("It must be zero or a positive integer")


@click.command()
@click.option(
    "--op-sa-name",
    "-n",
    "--sa",
    "sa_name",
    prompt=True,
    type=click.STRING,
    envvar="OP_SERVICE_ACCOUNT_NAME",
    required=True,
    default="enpass2onepassword",
    show_default=True,
    help="""
         The 1Password service account name.
         You chose this when creating the 1Password service account.
         
         Can also be supplied as environment variable 'OP_SERVICE_ACCOUNT_NAME'.
         """,
)
@click.option(
    "--op-sa-token",
    "-t",
    "--token",
    "sa_token",
    prompt=True,
    hide_input=True,
    type=click.STRING,
    envvar="OP_SERVICE_ACCOUNT_TOKEN",
    required=True,
    help="""
         The 1Password service account token. It was shown to you when you created the 1Password service account.
         
         Can also be supplied as environment variable 'OP_SERVICE_ACCOUNT_TOKEN'.
         """,
)
@click.option(
    "--op-vault",
    "-o",
    "--vault",
    "op_vault",
    prompt=True,
    type=click.STRING,
    envvar="OP_VAULT",
    required=True,
    default="Enpass",
    show_default=True,
    help="""
         The name of the 1Password vault.
         All Enpass items will be created in that 1Password vault.
         This 1Password vault must be empty!
         Also, the service account must have write permissions to it.
         
         Can also be supplied as environment variable 'OP_VAULT'.
         """,
)
@click.option(
    "--ignore-non-empty-vault",
    "ignore_non_empty",
    is_flag=True,
    help="""
         By default, this tool will stop if it detects that there are already items in a vault.
         Use this flag to ignore this behavior and continue, even if there are already items in the given vault.
         If you use this, you should definitely make a sound backup of the vault before the import!
         """,
)
@click.option(
    "--no-confirm",
    "no_confirm",
    is_flag=True,
    help="""
         By default, this tool will stop before importing anything to 1Password,
         and you need to confirm the import.
         Use this flag to ignore this behavior and import without further confirmation.
         """,
)
@click.option(
    "--no-wakelock",
    "no_wakelock",
    is_flag=True,
    help="""
         By default, this tool will prevent the computer to go to sleep while the import is running.
         Use this flag to disable this behavior.
         
         When this flag is defined, then the computer might go to sleep and interrupt your import.
         The import is usually resumed, when your computer resumes from sleep.
         The result is that you won't make the best use of the 1Password rate limits.
         """,
)
@click.option(
    "--silent",
    is_flag=True,
    help="""
         By default, this tool will print status information while importing to 1Password.
         Use this flag to disable such reports.
         """,
)
@click.option(
    "--skip",
    type=click.INT,
    callback=is_zero_or_positive,
    default=0,
    show_default=True,
    help="""
         Skip the first number of items.
         This can be helpful to recover a failed import.
         """,
)
@click.option(
    "--op-rate-limit-hourly",
    "rate_limit_h",
    type=click.INT,
    callback=is_positive,
    default=100,
    show_default=True,
    help="""
         1Password enforces a write request rate limit per 1Password Service Account.
         The hourly rate limit as of 2025-01-01 is 100 requests per hour for private, family and team accounts
         and 1'000 requests per hour for Business accounts.
         
         \b
         See https://developer.1password.com/docs/service-accounts/rate-limits/ for more info.
         """,
)
@click.option(
    "--op-rate-limit-daily",
    "rate_limit_d",
    type=click.INT,
    callback=is_positive,
    default=1000,
    show_default=True,
    help="""
         1Password enforces a write request rate limit per 1Password Account.
         The daily limit as of 2025-01-01 is 1'000 requests per hour for private and family accounts,
         5'000 per day for Teams accounts and 50'000 requests per hour for Business accounts.
         
         \b
         See https://developer.1password.com/docs/service-accounts/rate-limits/ for more info.
         """,
)
@click.option(
    "--op-client-validity",
    "client_validity_s",
    type=click.INT,
    callback=is_positive,
    default=30 * 60,
    show_default=True,
    help="""
         This tool authenticates with the 1Password server in order to import entries.
         This authentication is only valid for a certain amount of time.
         With this parameter, you can adjust the time after which a this tool re-authenticates with the
         1Password server.
         
         The value is in seconds.
         """,
)
@click.argument(
    "enpass_json_export",
    default="export.json",
    type=click.File("rb"),
    envvar="ENPASS_FILE",
    required=True,
)
def main(
    enpass_json_export,
    sa_name,
    sa_token,
    op_vault,
    ignore_non_empty,
    no_confirm,
    silent,
    skip,
    no_wakelock,
    rate_limit_h,
    rate_limit_d,
    client_validity_s,
):
    """Adds items from an Enpass JSON export to a 1Password vault through the 1Password API."""
    asyncio.run(
        migrate(
            enpass_json_export,
            sa_name,
            sa_token,
            op_vault,
            ignore_non_empty,
            no_confirm,
            silent,
            skip,
            no_wakelock,
            rate_limit_h,
            rate_limit_d,
            client_validity_s,
        )
    )


if __name__ == "__main__":
    main()
