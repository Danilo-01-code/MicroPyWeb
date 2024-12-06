from micropyweb.core import MicroPyWeb 
from micropyweb.templating import render_response

app = MicroPyWeb()
app.config["DEBUG"] = True

@app.route()
def index():
    return render_response("index.html", name = "Bob")

@app.route("/examples",methods=["GET","POST"])
def example(request):
    if request.method == "GET":
        return render_response("form.html")
    name = request.POST.get("name")
    return render_response("result.html", name= name)


@app.error_handler(404)
def error_404():
    return "something wrong..."



                    
if __name__ == "__main__":
    # You also can run a development server with 
    # >> micropyweb run 
    # using the micropyweb cli
    app._run()

