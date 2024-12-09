import os
import ast
from typing import Union,Tuple
from random import randint
import string
import json
from webob import Response


def find_app_instance(class_name: str = "MicroPyWeb") -> Union[Tuple[str,str],None]:
    """Find an application installed under a given class_name and its respective file path"""

    directory = os.getcwd() 

    for file in os.listdir(directory):
        if file.endswith(".py"):
            file_path = os.path.join(directory, file)
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            for node in (n for n in ast.walk(tree) if isinstance(n, ast.Assign)):
                if (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == class_name):
                    return node.targets[0].id, file_path
    return None


def generate_secret_key():
    """This function generate a secret key, duh"""
    char = list(string.ascii_letters) + list(string.digits)
    secret_key = []

    for i in range(32):
        secret_key.append(char[randint(0,len(char)-1)])

    print(''.join(secret_key))