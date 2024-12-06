from wsgiref.simple_server import make_server
from typing import List
from webob import Request, Response
import traceback
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from micropyweb.request_messages import ColorWSGIRequest, color_text_red


class MicroPyWeb: #TODO config #TODO jsonfy
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
        self.error_funcs = {}
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
        
        def route_decorator(func):
            self.routes[path] =   {
            "handler": func,
            "methods": methods,
            }
            return func
        
        return route_decorator
    
    def handle_request(self, environ):
        """
        Manipulate the request and return a WSGI response
        """
        request = Request(environ)
        path = request.path

        route_info = self.routes.get(path)
        if not route_info:
           return self.not_found(path)

        handler = route_info["handler"]
        methods = route_info["methods"]

        try:
            if "POST" not in methods:
                response_body = handler() #if the method is GET, the request parameter it's not necessary
            else:
                response_body = handler(request)
            return Response(body=response_body, status=200, content_type="text/html")
        except Exception as e:
            return self.internal_server_error(e)
        
    def error_handler(self, status: int):
        """
        Decorator to register a function to override MicroPyWeb's default error handlers

        Parameters:
        - status (int): the http status code to be override

        Returns:
        - function: The decorator function that takes a custom error handler function as its argument.

        Example usage:
        @error_handler(404)
        def not_found_error():
            return "Something Wrong..."

        """
        def error_decorator(func):
            self.error_funcs[status] = func
            return func

        return error_decorator

    def __call__(self, environ, start_response) -> List[bytes]:
        """
        This method is invoked by the WSGI server, 
        passing the request environment and a callback for starting the HTTP response.

        Parameters:
        - environ (dict): A dictionary containing information about the request environment, 
        such as HTTP headers, query parameters, and server information.
        - start_response (Callable): A callable provided by the WSGI server used to initiate the HTTP response.

        Returns:
        - list[bytes]: An iterable (commonly a list) of byte strings representing the body of the HTTP response.
        """
        response = self.handle_request(environ)
        return response(environ, start_response)


    def _run(self, host='localhost',port=8000) -> None:
        """
        Runs a development server with a given host and port, method can be used by the
        MicroPyWeb cli
        """
        observer = None
        try:
            server = make_server(host,port, self, handler_class=ColorWSGIRequest)
                
            print("Debug mode: ", end="")
            if self.config["DEBUG"]: 
                print(True) 

                # Ativate watchdog to monitorate python files
                event_handler = FileSystemEventHandler()
                event_handler.on_modified = self._on_modified
                observer = Observer() 
                observer.schedule(event_handler, path='.', recursive=True)
                observer.start()
            else: 
                print(False)

            print(f"Server initialized in http://{host}:{port}", color_text_red("(Ctrl + C to quit)"))

            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped successfuly.")
        finally:
             if observer is not None:
                observer.stop()
                observer.join()

    def _on_modified(self, event):
        """
        Restart server for each event in your user project file in DEBUG mode True
        """
        if not event.is_directory and event.src_path.endswith(".py"):
            logging.info(f"Change in the file: {event.src_path}")


    def not_found(self, path):
        handler = self.error_funcs.get(404)
        if handler:
            return Response(handler(),status=404)
        
        body = "<h1>Not Found</h1>"
        if self.config["DEBUG"]:
            body += "<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again</p>"
            logging.error(color_text_red(f"404 Not Found - Requested URL: {path}")) 
        
        return Response(body, status=404)

    def internal_server_error(self, e):
        handler = self.error_funcs.get(500)
        if handler:
            return Response(handler(),status=500)
        
        body = f"<h1>Internal Server Error<h1>\n {str(e)}"
        if self.config["DEBUG"]:
            body += "<h2>Traceback (most recent call last):</h2>"
            body += f"<pre>{traceback.format_exc()}</pre>"
            logging.error(color_text_red(f"Traceback (most recent call last):\n{traceback.format_exc()}"))

        return Response(body, status=500)