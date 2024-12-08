from wsgiref.simple_server import WSGIRequestHandler
import re

class ColorWSGIRequest(WSGIRequestHandler):
    COLOR_RESET = "\033[0m"
    COLORS = {
        "200": "\033[32m",
        "404": "\033[33m",
        "500": "\033[31m",
    }
    def log_message(self,format,*args):
        """
        Log an custom arbitrary message.

        determines colors for each log
        """
        message = format % args

        color = self.COLOR_RESET
        for status_code, curr_color in self.COLORS.items():
            if re.search(status_code, message):
                color = curr_color
                break
        
        print(f"{color}{message}{self.COLOR_RESET}")


def color_text_red(text):
    """make a given text red with ANSI color"""
    red = "\033[31m"
    reset = "\033[m"
    return f"{red}{text}{reset}"

def color_text_green(text):
    """make a given text green with ANSI color"""
    red = "\033[32m"
    reset = "\033[m"
    return f"{red}{text}{reset}"