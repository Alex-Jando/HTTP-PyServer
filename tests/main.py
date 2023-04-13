from server import Routes, text, run

@Routes.route(path = '/')
def home(request):

    return text(text = 'Hello, world!')

if __name__ == '__main__':

    run()