# Micorpyweb

Micropyweb is a minimalist WSGI aplication, is simple and inspired in Flask and FastApi sintax

## A simple wxample

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