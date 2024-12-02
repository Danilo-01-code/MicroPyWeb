import os
import re
import click

def find_app_instance(class_name: str = "MicroPyWeb"): #TODO documentation
    """Search for an instance of the specified class in Python files in the current directory."""

    # Regex pattern to find the variable that instantiates the specified class (e.g., MicroPyWeb or any other class)
    pattern = r'(\w+)\s*=\s*' + re.escape(class_name) + r'\s*\('  # Looks for something like 'app = MicroPyWeb()'

    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        match = re.search(pattern, content) 

                        if match:
                            instance = match.group(1)

                            with open(path, 'r', encoding='utf-8') as file_exec:
                                code = file_exec.read()
                                # Remove 'if __name__ == "__main__":' block to ensure code is executed
                                code = re.sub(r"if __name__\s*==\s*['\"]__main__['\"]\s*[:].*", "", code)
                                exec(code, globals()) 

                            if instance in globals():
                                return globals()[instance]  
                            else:
                                click.echo(f"Could not find the instance for {instance} in {path}")
                                return None

                except Exception as e:
                    raise Exception(f"Could not read the file {path}: {e}")

    return None  
