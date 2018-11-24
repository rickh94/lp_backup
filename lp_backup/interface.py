import click
import os
from pathlib import Path

from lp_backup import Runner

USER_HOME = os.path.expanduser('~')


@click.group()
@click.option('-c', "--config", help="Path to config file",
              default=f"{USER_HOME}/.config/lp_backup.yml")
@click.pass_context
def cli(ctx, config):
    ctx.obj = dict()
    ctx.obj["CONFIG"] = Path(config)


@cli.command(help="Backup lastpass based onf config file")
@click.pass_context
def backup(ctx):
    runner = Runner(ctx.obj["CONFIG"])
    backup_file_name = runner.backup()
    print(f"New backup is {backup_file_name}")


@cli.command(help="Restore csv file based on config file.")
@click.pass_context
def restore(ctx):
    runner = Runner(ctx.obj["CONFIG"])
    restore_file_path = runner.restore()
    print(f"Restored file is {restore_file_path}. It is NOT encrypted, "
          f"be sure to keep it safe and delete it when not needed.")

