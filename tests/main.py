from server import Routes, file, run

@Routes.route(path = '/')
def home(request):

    return file(data='Hello, World!',
                extension='html')

if __name__ == '__main__':

    run()