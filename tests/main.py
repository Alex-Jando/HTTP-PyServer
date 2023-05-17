import server

app = server.Server()

@app.route('/')
def _(request):

    return 'Hello, world!'

with app:
    
    app.wait('Press Enter to continue...')