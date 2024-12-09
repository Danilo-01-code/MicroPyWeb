from micropyweb.core import MicroPyWeb
from micropyweb.templating import render_response

# MicroPyWeb instance initalization example
app = MicroPyWeb()
app.config["DEBUG"] = True

# root page example
@app.route()
def index():
    return render_response("index.html")

# post and get method with html templates example
@app.route("/examples",methods=["GET","POST"])
def example(request):
    if request.method == "GET":
        return render_response("form.html")
    name = request.POST.get("name")
    return render_response("result.html", name= name)

# jsonfy implementation example
@app.route("/jsonfy")
def jsonfy_example():
    app.jsonfy = True # when the parameter jsonfy is True, every py dict turns into a json file
    data = {"Message":"Hello World", "Situation":"Sucess"}
    return data

# dinamic routing example
@app.route("/users/<int:pk>", dinamic_route = True)
def user(pk):
    return f"User ID: {pk}"

# set and get cookie implementation
@app.route("/setcookie")
def setcookie():
   pass

@app.route("/getcookie")
def getcookie():
   pass

# error handler implementation
#@app.error_handler(404)
#def error_404():
#    return "something wrong..."


if __name__ == "__main__":
    # You also can run a development server with 
    # >> micropyweb run 
    # using the micropyweb cli
    app._run()

