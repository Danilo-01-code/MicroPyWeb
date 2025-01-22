# Micorpyweb

Micropyweb is a minimalist WSGI aplication, is simple and inspired in Flask and FastApi syntax

## A simple example

```python
from micropyweb.core import MicroPyWeb
from micropyweb.templating import render_response

# MicroPyWeb instance initalization 
app = MicroPyWeb()

# root page 
@app.route()
def index(): 
    return render_response("index.html")
```

to see more examples check the dir 'examples'
