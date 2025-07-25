import logging
import json
import os
from server import Server, ResponseCodes, ResponseMessages, Cache, CacheItem, render

logger = logging.getLogger("HTTP-PyServer-Example")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(console_handler)

cache = Cache("example_cache", reset_on_update=True)

form_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Form Example</title>
</head>
<body>
    <h2>Submit Your Name</h2>
    <form method="POST" action="/submit">
        <input type="text" name="username" placeholder="Enter your name" required>
        <input type="submit" value="Submit">
    </form>
</body>
</html>
"""

home_html = """
<!DOCTYPE html>
<html>
<head>
    <title>HTTP-PyServer Example</title>
</head>
<body>
    <h1>Welcome to HTTP-PyServer Example!</h1>
    <ul>
        <li><a href="/json?num=3">JSON Response</a></li>
        <li><a href="/form">HTML Form</a></li>
        <li><a href="/wildcard/12345">Wildcard Route Example</a></li>
        <li><a href="/cache">Cache Example</a></li>
        <li><a href="/session">Session Example</a></li>
        <li><a href="/ip">Show My IP</a></li>
    </ul>
</body>
</html>
"""

server = Server(
    host="127.0.0.1",
    port=8080,
    logger=logger,
    static_dir="static/",
    sessions_expire_after=60
)

@server.route("/")
def root(request):
    return render.text(home_html, filetype="html")

@server.route("/json")
def json_route(request):
    data = {
        "message": "Hello, JSON!",
        "your_ip": request.address[0],
        "path": request.path,
        "query": request.query
    }
    return render.text(json.dumps(data), filetype="json")

@server.route("/form")
def form_route(request):
    return render.text(form_html, filetype="html")

@server.route("/submit", include_session=True)
def submit_route(request, session):
    if request.method == "POST":
        form_data = request.form()
        username = form_data.get("username", [""])[0]
        session.set("username", username)
        return render.text(f"<h2>Hello, {username}!</h2><a href='/session'>Go to session page</a>", filetype="html")
    return render.text(form_html, filetype="html")

@server.route("/wildcard/%id%")
def wildcard_route(request, id):
    return render.text(f"<h2>Wildcard Route: ID = {id}</h2>", filetype="html")

@server.route("/cache")
def cache_route(request):
    if not cache.get("visits"):
        cache.add(CacheItem("visits", 1, expire=10))
    else:
        cache.add(CacheItem("visits", cache.get("visits") + 1, expire=10))
    visits = cache.get("visits")
    return render.text(f"<h2>Cache Example</h2><p>This page has been visited {visits} times (resets after 10s of no visits).</p>", filetype="html")

@server.route("/session", include_session=True)
def session_route(request, session):
    username = session.get("username")
    if username:
        msg = f"<h2>Session: Welcome back, {username}!</h2>"
    else:
        msg = "<h2>Session: No username found. Go to <a href='/form'>form</a> to submit your name.</h2>"
    return render.text(msg, filetype="html")

@server.route("/ip")
def ip_route(request):
    return render.text(f"<h2>Your IP address is: {request.address[0]}</h2>", filetype="html")

if __name__ == "__main__":
    with server:
        server.wait("Press enter to stop the server...")