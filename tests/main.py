import server

app = server.Server()

@app.route('/')
def _(request):

    return 'Hello, World!'

with app:
    
    app.wait('Press Enter to continue...')