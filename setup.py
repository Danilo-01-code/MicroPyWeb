from setuptools import setup, find_packages

setup(
    name="micropyweb",
    version="0.1",
    description="A minimalist and modula micro framework",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages= find_packages(),
    install_requires=[
        "click==8.1.7",
        "WebOb==1.8.9",
        "Werkzeug==3.0.6",
        "watchdog==4.0.2",
        "Jinja2==3.1.4",

    ],
    python_requires='>=3.6',
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={  
        "console_scripts": [
            "micropyweb = micropyweb.cli:cli",
        ],
    },
)

