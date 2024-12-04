from wsgiref.simple_server import make_server
from typing import List
from webob import Request, Response
from urllib.parse import parse_qs
import traceback
import logging


class MicroPyWeb: #TODO config #TODO post method properly #TODO jsonfy
    """
    A WSGI aplication with a simple implementation based on Flask and FastApi

    for usage you should instanciate a object to this central class:
    
        from micropyweb import MicropyWeb
        app = MicropyWeb()
    """

    config = {
        "DEBUG":False,
        "SECRET_KEY":None,
    }

    def __init__(self):
        self.routes = {}
        self.middlewares = []
        self.config = MicroPyWeb.config
        self.methods = ["GET","POST"]

    def route(self, path: str = "/",methods: list = ["GET"]):
        """
        A decorator to tell the class what URL should trigger your view function
        
        Usage:
            @app.route()
            def index():
                return "Hello World!" 

        Parameters:
        -path: contain the URL (default: "/")
        -method:contain the http verb for the URL (default: "GET")       
        """
        
        for method in methods:
            if method not in self.methods:
                raise ValueError(f"Method {method} is not allowed.")
        
        def decorator(func):
            self.routes[path] =   {
            "handler": func,
            "methods": methods,
            "response": Response,
            }
            return func
        
        return decorator
    
    def handle_request(self, request):
        """
        Manipulate the request and return a WSGI response
        """
        path = request.path
        method = request.method

        route_info = self.routes.get(path)
        if not route_info:
           return self.not_found(path)

        handler = route_info["handler"]

        if method in ['POST','PUT']:
            try:
                body = request.environ['wsgi.input'].read(int(request.headers.get('Content-Length',0)))
                request.data = parse_qs(body.decode())
            except Exception:
                request.data = {}

        try:
            response_body = handler()
            return Response(body=response_body, status=200, content_type="text/html")
        except Exception as e:
            return self.internal_server_error(e)
        
    def error_handler(self, error: int):
        """
        Register a function to override MicroPyWeb's default error handlers
        """
        pass

    def __call__(self, environ, start_response) -> List[bytes]:
        """
        Handles incoming WSGI requests. This method is invoked by the WSGI server, 
        passing the request environment and a callback for starting the HTTP response.

        Parameters:
        - environ (dict): A dictionary containing information about the request environment, 
        such as HTTP headers, query parameters, and server information.
        - start_response (Callable): A callable provided by the WSGI server used to initiate the HTTP response.

        Returns:
        - list[bytes]: An iterable (commonly a list) of byte strings representing the body of the HTTP response.
        """
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)


    def _run(self, host='localhost',port=8000) -> None:
        """
        Runs a development server with a given host and port, method can be used by the
        MicroPyWeb cli
        """
        try:
            server = make_server(host,port, self)
            print("Debug mode: ", end="")
            if self.config["DEBUG"]: 
                print(True) 
            else: 
                print(False)

            print(f"Server initialized in http://{host}:{port} (Ctrl + C to quit)")
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped successfuly.")

    def not_found(self, path):
        body = "<h1>Not Found</h1>"
        if self.config["DEBUG"]:
            body += "<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again</p>"
            logging.error(f"404 Not Found - Requested URL: {path}") 
        
        return Response(body, status=404)

    def internal_server_error(self, e):
        body = f"<h1>Internal Server Error<h1>\n {str(e)}"
        if self.config["DEBUG"]:
            body += "<h2>Traceback (most recent call last):</h2>"
            body += f"<pre>{traceback.format_exc()}</pre>"
            logging.error(f"Traceback (most recent call last):\n{traceback.format_exc()}")

        return Response(body, status=500)