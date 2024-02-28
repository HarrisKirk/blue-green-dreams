import typer
from common import log_level_arg
import switch

switch_app = typer.Typer()

@switch_app.command()
def delete(env, log_level: str  = log_level_arg):
    switch.delete(env, log_level)

@switch_app.command()
def create(env, log_level: str  = log_level_arg):
    switch.create(env,log_level)

@switch_app.command()
def view(env, log_level: str  = log_level_arg):
    switch.view(env,log_level)
