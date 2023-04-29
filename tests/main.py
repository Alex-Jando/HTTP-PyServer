from server import Routes, text, run

@Routes.route(path = '/')
def home(request):

    return text('Hello, World!')

if __name__ == '__main__':

    run()