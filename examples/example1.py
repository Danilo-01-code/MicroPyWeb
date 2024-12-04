from micropyweb.core import MicroPyWeb
from micropyweb.templating import render_response

app = MicroPyWeb()
app.config["DEBUG"] = True

@app.route(methods = ["GET","POST"])
def index():
    return render_response("index.html", name = "Bob")

if __name__ == "__main__":
    # You also can run a development server with 
    # >> micropyweb run 
    # using the micropyweb cli
    app._run()

