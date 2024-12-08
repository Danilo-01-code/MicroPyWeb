from jinja2 import Environment, FileSystemLoader

def render_response(
        template_name:str,
        template_folder = "templates",
        **context
) -> str:
    """
    Render a template with "template_name" name and a given context for Jinja2 engine

      Parameters:
    - template_name: the template file name to be rendered (e.g., "index.html").
    - template_folder: the folder where the template files are located (default is "templates").
    - context: key-value pairs of variables to be passed into the Jinja2 template.

    Returns:
    - A string containing the rendered HTML or content from the template.
    """

    jinja2_env = Environment(
        loader = FileSystemLoader(template_folder),
        autoescape = True
    )

    template = jinja2_env.get_template(template_name)

    return template.render(context)