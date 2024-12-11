import unittest
from micropyweb.core import MicroPyWeb, set_cookie
from micropyweb.templating import render_response
from webtest import TestApp


class SimpleTestCase(unittest.TestCase):

    def setUp(self):
        app = MicroPyWeb()

        @app.route()
        def index():
            return "Test"
        
        @app.route("/notallowed", methods = ["P"])
        def not_allowed():
            return 
        
        @app.route("/force500")
        def force_error():
            return Exception("bla")
        
        @app.route("/template")
        def templating():
            return render_response("test.html")
        
        @app.route("/json")
        def jsonfy_example():
            app.jsonfy = True 
            data = {"Message":"Hello World", "Situation":"Sucess"}
            return data
        
        @app.route("/double/path")
        def double_path():
            return "Correct"  
        
        self.test_app = TestApp(app)

    def test_homepage(self):
       response = self.test_app.get("/")

       self.assertEqual(response.status_code, 200)
       self.assertEqual("Test",response.text)

    def test_not_found(self):
        response = self.test_app.get("/notfound", expect_errors=True)

        self.assertEqual("<h1>Not Found</h1>", response.text)
        self.assertEqual(response.status_code,404)
    
    def test_method_not_allowed(self):
        response = self.test_app.get("/notallowed", expect_errors=True)

        self.assertEqual("<h1>Not Allowed Method</h1>", response.text)
        self.assertEqual(response.status_code,405)

    def test_internal_server_error(self):
        response = self.test_app.get("/force500", expect_errors=True)

        self.assertEqual(f"<h1>Internal Server Error</h1>\n object of type 'Exception' has no len()", response.text)
        self.assertEqual(response.status_code,500)

    def test_templating_render(self):
        response = self.test_app.get("/template")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(f"<h1>Testing...</h1>",response.text)

    def test_json(self):
        response = self.test_app.get("/json")

        self.assertEqual(response.status_code,200)
        self.assertEqual(response.content_type, 'application/json')

        response_json = response.json

        self.assertEqual(response_json["Message"], "Hello World")
        self.assertEqual(response_json["Situation"], "Sucess")

    def test_double_path(self):
        response = self.test_app.get("/double/path")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(f"Correct",response.text)


if __name__ == "__main__":
    unittest.main()