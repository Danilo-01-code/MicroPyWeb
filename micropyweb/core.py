from wsgiref.simple_server import make_server
from typing import List
from webob import Request, Response
import traceback
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from micropyweb.request_messages import ColorWSGIRequest, color_text_red, color_text_green
from micropyweb.utils import normalize
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import NotFound
import json


class MicroPyWeb:
    """
    A WSGI minimalist and modular aplication.

    for usage you should instanciate a object to this central class:
    
        from micropyweb import MicropyWeb
        app = MicropyWeb()
    
    for more informations se example1.py in examples and the README.md
    """

    config = {
        "DEBUG":False,
    }

    def __init__(self):
        self.cookie = {}
        self.route_info = {}
        self.error_funcs = {}
        self.headers = {}
        self.jsonfy = False
        self.request = Request
        self.config = MicroPyWeb.config
        self.dynamic_route = {}
        self.allowed_methods = {"GET","POST","PUT"}
        self.methods = {}

    def route(self, path: str = "/",methods: list = ["GET"], cookie = ""):
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
        self.cookie[normalize(path)] = cookie

        def route_decorator(func):
            self.methods[normalize(path)] = methods

            if "<" in path and ">" in path: # The dynamic routes are defined with angle brackets 
                  self.dynamic_route[normalize(path)] = Map([Rule(path, endpoint=func, methods=methods)])
            else:
                self.route_info[path] = {
                    "handler": func,
                    "methods": methods,
                }  
            
            return func
          
        return route_decorator 
    
    def get(self, path):
        return self.route(path)
    
    def _handle_dynamic_routing(self,environ, path, request):
        """ 
        Manipulate requests with dynamic routing.
        """

        try:
            adapter = self.dynamic_route[normalize(path)].bind_to_environ(environ)
            endpoint, args = adapter.match()
            handler = endpoint 
            if "POST" not in self.methods and "PUT" not in self.methods:
                response_body = handler(**args) 
            else:
                response_body = handler(request, **args)

            if self.jsonfy: 
                return self._jsonfy(response_body)
            return Response(body=response_body, status=200, content_type="text/html")
        
        except KeyError:
            return self.not_found(path)
        except NotFound:
            return self.not_found(path)
        except Exception as e:
            return self.internal_server_error(e)
  
    def _handle_request(self, environ):
        """
        Manipulate the request and return a WSGI response with Webob Response object.

        This method can return text, html or json for the Browser
        
        Note:
        - To transform your python dict in a json file the MicroPyWeb jsonfy attribute should
        be True
        """
        try:
            request = self.request(environ)
            path = request.path
            methods = self.methods[normalize(path)]
            for method in methods:
                if method not in self.allowed_methods:
                    return self.not_allowed_method(method)
            
            route_info = self.route_info.get(path)
        
            if not route_info:
                return self._handle_dynamic_routing(environ, path, request)

            handler = route_info["handler"]
            
            if self.cookie[normalize(path)] != "":
                cookie_value = get_cookie(environ, self.cookie[normalize(path)])
                response_body = handler(cookie_value)
                return Response(body=response_body, status=200, content_type="text/html")
            
            if "POST" not in methods and "PUT" not in methods:
                response_body = handler() #if the method is only GET, the request parameter it's not necessary
                if isinstance(handler(),Response):
                    return handler()
            else:
                response_body = handler(request)
                if isinstance(handler(request),Response):
                    return handler(request)

            if self.jsonfy: 
                return self._jsonfy(response_body)
                        
            return Response(body=response_body, status=200, content_type="text/html")
        except KeyError:
            return self.not_found(path)
        except Exception as e:
            return self.internal_server_error(e)
        
    def _jsonfy(self,response_body):
        """
        Transform the python dict response_body in a json file.
        """
        if isinstance(response_body,dict):
            json_data = json.dumps(response_body) 
            self.jsonfy = False
            return Response(body=json_data,status=200,content_type="application/json; charset=utf-8")
        
        raise ValueError("The return of the view function should be a dict when jsonfy = True")
        
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
        response = self._handle_request(environ)
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
                print(color_text_green("True")) 

                # Ativate watchdog to monitorate python files
                event_handler = FileSystemEventHandler()
                event_handler.on_modified = self._on_modified
                observer = Observer() 
                observer.schedule(event_handler, path='.', recursive=True)
                observer.start()
            else: 
                print(color_text_red("False"))

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
    

    def not_found(self, path:str):
        """
        Handles HTTP 404 (Not Found) errors.

        Parameters:
        -path (str): the path that micropyweb tried to access

        Notes:
        - If a custom view function is defined using the `error_handler()` decorator,
        it will override this default `not_found` behavior.
        - When `DEBUG` is set to True in the configuration, this function will display
        additional details about the error to assist in development. This behavior
        will not apply if the function is overridden using `error_handler()`.
        """

        handler = self.error_funcs.get(404)

        if handler:
            return Response(handler(),status=404)
        
        body = "<h1>Not Found</h1>"
        if self.config["DEBUG"]:
            body += "<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again</p>"
            logging.error(color_text_red(f"404 Not Found - Requested URL: {path}")) 
        
        return Response(body, status=404)

    def not_allowed_method(self, method):
        """
        Handles HTTP 405 Method nNot allowed errors.

        Parameters:
        -method (str): the disallowed method that the system identified
        """

        handler = self.error_funcs.get(405)

        if handler:
            return Response(handler(),status=405)
        
        body = "<h1>Not Allowed Method</h1>"
        if self.config["DEBUG"]:
            body += f"<p>Method: '{method}'</p>"
            logging.error(f"The method: {method} is not allowed in MicroPyWeb")

        return Response(body,status = 405)
 

    def internal_server_error(self, e):
        """
        Handles HTTP 500 (Internal server error).

        This function is invoked when an unhandled exception occurs in the application, 
        resulting in a server error response.

        Parameters:
        - e (Exception): The exception object that triggered the error.

        Notes:
        - If "DEBUG" is set to True in the configuration, this function may include a detailed 
        traceback in the response to assist in debugging.
        - You can override this behavior by defining a custom view function using the 
        `error_handler()` decorator.
        """

        handler = self.error_funcs.get(500)

        if handler:
            return Response(handler(),status=500)
        
        body = f"<h1>Internal Server Error</h1>\n {str(e)}"
        if self.config["DEBUG"]:
            body += "<h2>Traceback (most recent call last):</h2>"
            body += f"<pre>{traceback.format_exc()}</pre>"
            logging.error(color_text_red(f"Traceback (most recent call last):\n{traceback.format_exc()}"))

        return Response(body, status=500)


def set_cookie(cookies: dict):
    """
    Configurate the given cookies in a Response object.
    """
    response = Response()

    for cookie_name, cookie_value in cookies.items():
        response.set_cookie(
            name=cookie_name,
            value=cookie_value,
            max_age=3600,  
            secure=True,   
            httponly=True,
            path="/"      
        )
    return response

def get_cookie(environ, cookie_name: str) -> str:
    """
    Recuperates a specific cookie with Request object
    """
    request = Request(environ)
    return request.cookies.get(cookie_name)