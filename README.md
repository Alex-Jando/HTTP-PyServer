# Project Description

HTTP-PyServer is a simple, and extremly light-weight solution to create powerful projects relying on the web with few lines of code. It uses python built-in packages to host server's and then handle http requests, as well as responses. It's extremely customizable, and allows you do to almost everything you might want.

HTTP-PyServer is also very flexible on your project layout. It ensures security by allowing you to specify which files to send, and to where. HTTP-PyServer allows you to do everything you need whilst keeping hands relaxed with as few lines of code as possible.

# Installing

Install HTTP-PyServer using pip from the command line.

```
python -m pip install HTTP-PyServer
```

# Simple Example

```
# Saved as "main.py"
from server import Routes, text, run

@Routes.route(path = '/')
def home(request):

    return text(text = 'Hello, world!')

if __name__ == '__main__':

    run()
```

```
$ python main.py
Press enter to exit...

```

# Contributing

Look on github, and create a fork of HTTP-PyServer. Submit, pull requests, and any features will be looked at, and potentially implemented.

# Used Packages

Although, no external packages were used, the following packages were imported. All packages are native in Python 3.11.2. Not tested on any other versions, however it should work.

- `threading`
- `socket`
- `sys`
- `logging`
- `os`
- `urllib`
- `mimetypes`
- `enum`