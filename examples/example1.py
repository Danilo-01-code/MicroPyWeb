from micropyweb.core import MicroPyWeb

app = MicroPyWeb()

@app.route("/")
def index():
    return "Hello World!"

if __name__ == "__main__":
    app._run()