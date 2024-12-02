import click
import importlib
from micropyweb.utils import find_app_instance
import os 
import sys

#This file contains all the command line functions
@click.group()
def cli():
    """command lines to run micropyweb framework"""
    pass

@click.command()
@click.option('--host',default='localhost',help='the host adress to run the server')
@click.option('--port',default=8000,help='the server port')
def run(host,port):
    """
    The run method will start a development server

    Usage in command line:
        micropyweb run app_module

    Parâmaters:
    -app_module: the Python file where your app instance is defined.
    -host: the host adress to bind the server (default: localhost).
    -port: the port to bind the server (default: 8000).
    """
    instance = find_app_instance()

    if not instance:
        raise ModuleNotFoundError("A module with a MicroPyWeb Instance was not found in the current dir")
    
    instance._run(host,port)
    


cli.add_command(run)

if __name__ == "__main__":
    cli()
