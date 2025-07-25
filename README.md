# Project Description

HTTP-PyServer is a simple, and extremely light-weight solution to create powerful projects relying on the web with the fewest lines of code. It uses python built-in packages to host server's and then handle http requests, as well as responses. It's extremely customizable, and allows you do to almost everything you might want.

HTTP-PyServer is also very flexible on your project layout. It ensures security by allowing you to specify which files to send, and to where. HTTP-PyServer allows you to do everything you need whilst keeping hands relaxed with as few lines of code as possible.

# Features

- Return various filetypes (HTML, CSS, JS, JSON, Images, Video)
- Get information from the users request (Headers, IP Addresses, Queries)
- Handle any HTTP request type
- Use a custom logger to record any server activity how you want
- Utilizes multi-threading to ensure quick response times
- Relies on **NO NON-NATIVE LIBRARIES** which leads to super quick runtimes
- Handle wildcard routes to access different ressources
- Cache information in the server and automaticall delete it after a certain time
- Store user data in sessions to identify profiles
- Integrate python code into your static files with templating

# Installing

Install HTTP-PyServer using pip from the command line.

```
python -m pip install HTTP-PyServer
```

# Simple Example

```
# Saved as "main.py"
import server

app = server.Server()

@app.route('/')
def _(request):

    return 'Hello, world!'

with app:
    
    app.wait('Press Enter to continue...')
```

```
$ python main.py
Press Enter to continue...

```

# Contributing

Look on github, and create a fork of HTTP-PyServer. Submit pull requests, and any features will be looked at and potentially implemented.

# Used Packages

Although, no external packages were used, the following packages were imported. All packages are native in `Python 3.7+`.

- `threading`
- `socket`
- `typing`
- `logging`
- `pathlib`
- `re`
- `time`
- `json`
- `urllib`
- `mimetypes`
- `enum`
- `ssl`
- `secrets`