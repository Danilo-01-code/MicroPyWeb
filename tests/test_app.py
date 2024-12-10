import unittest
from micropyweb.core import MicroPyWeb
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
        
        self.test_app = TestApp(app)

    def test_homepage(self):
       response = self.test_app.get("/")
       self.assertAlmostEqual(response.status_code, 200)
       self.assertIn("Test",response.text)

    def test_not_found(self):
        response = self.test_app.get("/notfound", expect_errors=True)
        self.assertIn("<h1>Not Found</h1>", response.text)
        self.assertAlmostEqual(response.status_code,404)
    
    def test_method_not_allowed(self):
        response = self.test_app.get("/notallowed", expect_errors=True)
        self.assertIn("<h1>Not Allowed Method</h1>", response.text)
        self.assertAlmostEqual(response.status_code,405)

    def test_internal_server_error(self):
        response = self.test_app.get("/force500", expect_errors=True)
        self.assertIn(f"<h1>Internal Server Error</h1>\n object of type 'Exception' has no len()", response.text)
        self.assertAlmostEqual(response.status_code,500)


if __name__ == "__main__":
    unittest.main()