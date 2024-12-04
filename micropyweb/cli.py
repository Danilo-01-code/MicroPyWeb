import click
import importlib
from micropyweb.utils import find_app_instance
import os 
import sys


@click.group()
def cli():
    """command lines to run micropyweb framework"""
    pass

@click.command()
@click.option('--host',default='localhost',help='the host adress to run the server')
@click.option('--port',default=8000,help='the server port')
def run(host,port):
    """
    Starts a development server for the MicroPyweb aplication.

    This method should be called in the directory containing the file with the MicroPyWeb instance.

    Usage in command line:
        micropyweb run 

    Parameters:
    -host: the host adress to bind the server (default: localhost).
    -port: the port to bind the server (default: 8000).
    """
    instance_name, file_path = find_app_instance()
  

    if not instance_name or not file_path:
        raise ModuleNotFoundError("A module with a MicroPyWeb Instance was not found in the current dir")
    

    with open(file_path, "r", encoding="utf-8") as f:
        exec(f.read(), globals()) 

    instance = globals().get(instance_name)

    if not instance:
        raise NameError(f"Instance '{instance_name}' was not found in the global scope")

    instance._run(host,port)
    

cli.add_command(run)

if __name__ == "__main__":
    cli()
