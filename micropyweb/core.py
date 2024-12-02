from wsgiref.simple_server import make_server

class MicroPyWeb: #TODO config
    """
    A WSGI aplication with a simple implementation based on Flask

    for usage you should instanciate a object to this central class:
    
    from micropyweb import MicropyWeb

    app = MicropyWeb()
    """
    def __init__(self):
        self.routes = {}

    def route(self, path = "/", method = "GET"):
        methods = ["GET","POST"]

        if method not in methods:
            raise ValueError("method not allowed")
        
        def decorator(func):
            #Add the function "func" to the dictionary whith "path" and "method" as key
            self.routes[(path,method)] = func
            return func
        
        return decorator
    
    def handle_requests():
        pass

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "/")
        func = self.routes.get((path, "GET"), self.not_found)  # Default to GET method
        response = func()
        start_response("200 OK", [("Content-type", "text/plain")])
        return [response.encode()]
    
    def _run(self, host='localhost',port=8000):
        try:
            server = make_server(host,port, self)
            print(f"Server initialized in http://{host}:{port}")
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped successfuly.")

    def not_found(self):
        return "Not Found 404"
