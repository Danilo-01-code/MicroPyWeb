from webtest import TestApp
from micropyweb.core import MicroPyWeb, set_cookie
from micropyweb.request_messages import color_text_green

test_app = MicroPyWeb()

@test_app.route("/setcookie")
def setcookie():
    cookie = {"username":"name"}
    response = set_cookie(cookie)
    response.text = "Cookie set"
    return response

@test_app.route("/getcookie", cookie="username")
def getcookie(cookie):
    return cookie

def test_setcookie():
    app = TestApp(test_app)  
    response = app.get('/setcookie')
    assert response.text == "Cookie set"
    print(color_text_green("Ok"))

def test_getcookie():
    app = TestApp(test_app)
    response = app.get('/setcookie')
    
    response = app.get('/getcookie', extra_environ={'HTTP_COOKIE': 'username=Name'})
    assert response.text == "Name"
    print(color_text_green("Ok"))

def main():
    test_setcookie()
    test_getcookie()

if __name__ == "__main__":
    main()