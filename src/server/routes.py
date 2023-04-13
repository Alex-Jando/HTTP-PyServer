import os

from . import responses
from . import request
from . import render

class Routes:

    routes: dict[str, callable] = {

        '/404': lambda request: f'''<!DOCTYPE html>

        <html>

        <head>
        <title>404 Not Found</title>
        </head>

        <body>

        <h1 style="text-align: center;">404 Not Found</h1>

        <p style="text-align: center;">Couldn't find any {request.path} endpoint.</p>

        </body>

        </html>'''.encode(encoding = 'utf-8', errors = 'ignore')

    }

    @classmethod
    def route(cls,
              *args,
              path: str,
              ressources: tuple[tuple[str, str]] = []) -> callable:
        '''Adds a route to the routes dictionary.'''

        for ressource_file_path, ressource_reference_path in ressources:

            ressource_reference_path = '/' + ressource_reference_path.strip('/')

            if not os.path.exists(ressource_file_path):

                cls.routes[ressource_reference_path] = \
                    lambda _: render.text(text = Routes.get_route('/404',
                                                   request = request),
                                          code = responses.ResponseCodes.NOT_FOUND,
                                          message = responses.ResponseMessages.NOT_FOUND)

            else:

                ressource = render.attachment(filepath = ressource_file_path)

                cls.routes[ressource_reference_path] = \
                lambda _, ressource = ressource: ressource

        def callable_route(route_function):

            cls.routes[path.rstrip('/')] = route_function

            return route_function
        
        return callable_route
    
    @classmethod
    def _get_wildcard_path(cls,
                           *args,
                           path: str,
                           request: request.Request) -> bytes:
        '''Gets a route with wildcard values.'''
    
        for route in cls.routes:

            if not len(route.split('/')) == len(path.split('/')):

                continue

            for sub_route, sub_path in zip(route.split('/'), path.split('/')):

                if (not sub_route == sub_path) \
                    and (not (sub_route.startswith('%') \
                            and sub_route.endswith('%'))):

                    break

            else:

                wildcard_values = []

                for sub_route, sub_path \
                    in zip(route.split('/'), path.split('/')):

                    if sub_route.startswith('%') and sub_route.endswith('%'):

                        wildcard_values.append(sub_path)

                return cls.routes[route](request,
                                         *wildcard_values)

        return render.text(text = Routes.get_route('/404',
                                                   request = request),
                           code = responses.ResponseCodes.NOT_FOUND,
                           message = responses.ResponseMessages.NOT_FOUND)

    @classmethod
    def get_route(cls,
                  *args,
                  path: str = '',
                  request: request.Request = request.Request()) -> bytes:
        '''Gets a route from the routes dictionary.'''

        if path in cls.routes:

            return cls.routes[path](request)

        else:

            return cls._get_wildcard_path(path = path,
                                          request = request)