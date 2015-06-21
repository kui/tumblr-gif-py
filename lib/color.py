RED = "\033[93m"
GREEN = "\033[92m"
DEFAULT = "\033[0m"

def print_g(s):
    print_with_color(GREEN, s)

def print_r(s):
    print_with_color(RED, s)

def print_with_color(ansi, s):
    print("".join([ansi, s, DEFAULT]))
