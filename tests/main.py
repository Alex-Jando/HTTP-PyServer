from server import Routes, run

@Routes.route('/')
def index(request):

    return 'Hello, World!'

if __name__ == '__main__':

    run()