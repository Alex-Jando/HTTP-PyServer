import os

from . import response_messages
from . import response_codes
from . import response
from . import request
from . import render

class Routes:
    '''Stores, sorts, and handles a collection of routes.'''

    def __init__(self) -> None:

        self._routes: dict[str: callable] = {
            '/404': lambda request: render.text('''<!DOCTYPE html>

<html>

<head>
<title>404 Not Found</title>
</head>

<body>

<h1 style="text-align: center;">404 Not Found</h1>

<hr>

<p style="text-align: center;">HTTP-PyServer</p>

</body>

</html>''',
filetype='html',
code = response_codes.ResponseCodes.NOT_FOUND,
message = response_messages.ResponseMessages.NOT_FOUND)
    }

    def route(self,
              path: str,
              *,
              ressources: dict[str: str] = {}) -> callable:
        '''Adds a route to the routes dictionary.'''

        for ressource_file_path, ressource_reference_path in ressources.items():

            ressource_reference_path = '/' + ressource_reference_path.strip('/')

            if not os.path.exists(ressource_file_path):

                self._routes[ressource_reference_path] = \
                    lambda _: self._routes['/404'](request = request.Request())

            else:

                ressource = render.attachment(filepath = ressource_file_path)

                self._routes[ressource_reference_path] = \
                lambda _, ressource = ressource: ressource

        def callable_route(route_function):

            self._routes[path.rstrip('/')] = route_function

            return route_function
        
        return callable_route
    
    def _get_wildcard_path(self,
                           path: str,
                           *,
                           request: request.Request) -> bytes:
        '''Gets a route with wildcard values.'''
    
        for route in self._routes:

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

                message =  self._routes[route](request,
                                         *wildcard_values)
                
                if isinstance(message, str):

                    return bytes(render.text(message))
                
                elif isinstance(message, bytes):

                    return message
                
                elif isinstance(message, response.Response):

                    return bytes(message)
                
                else:

                    raise TypeError(f'Expected function for {request.path} \
to return str, bytes, or Response, got {type(message)}.')

        return self._get_route('/404', request = request)

    def _get_route(self,
                  path: str,
                  *,
                  request: request.Request = request.Request()) -> bytes:
        '''Gets a route from the _routes dictionary.'''

        if path in self._routes:

            message = self._routes[path](request)

            if isinstance(message, str):

                return bytes(render.text(text = message))
            
            elif isinstance(message, bytes):

                return message
            
            elif isinstance(message, response.Response):

                return bytes(message)
            
            else:

                raise TypeError(f'Expected function for {request.path} \
to return str, bytes, or Response, got {type(message)}.')

        else:

            return self._get_wildcard_path(path = path,
                                          request = request)