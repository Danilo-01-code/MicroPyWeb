import click
from micropyweb.utils import find_app_instance
import code
from micropyweb.request_messages import color_text_red

@click.group()
def cli():
    """
    A command line interface to help in the application development with MiroPyWeb.
    """
    pass

@click.command()
@click.option('--host',default='localhost',help='the host adress to run the server')
@click.option('--port',default=8000,help='the server port')
def run(host:str,port:int):
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

@click.command()
@click.option('--file',help='the file to import objects to shell',required=True)
def shell(file:str):
    """
    Launch a interactive shell with all objects in a given file.

    the file should be in a format that support object loading,
    such a python file.

    Usage in command line:
        micropyweb shell --file file.py

    Parameters:
    -file: the file to take objects for the shell.
    """
    local_objects = {}
    try:
        with open(file, 'r') as f:
            exec(f.read(), local_objects)
    except Exception as e:
        print(f"Can´t open the file: {e}")
        return

    console = code.InteractiveConsole(local_objects)
    
    banner = f"Welcome to the micropy web shell, {color_text_red('(use the quit() or exit() function to exit the shell)')}"
    console.interact(banner=banner)

commands = [run,shell]


for command in commands:
    cli.add_command(command)

if __name__ == "__main__":
    cli()