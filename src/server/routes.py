import pathlib

from . import response_messages
from . import response_codes
from . import response
from . import request
from . import render

class Routes:
    '''Stores, sorts, and handles a collection of routes.'''

    def __init__(self) -> None:

        self._root = None

        self._root_uses_session = False

        self._session_routes: list = []

        self._routes: dict[str: callable] = {

            self._404route: lambda request: render.text('''<!DOCTYPE html>

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
message = response_messages.ResponseMessages.NOT_FOUND),

            self._500route: lambda request: render.text('''<!DOCTYPE html>

<html>

<head>
<title>500 Internal Server Error</title>
</head>

<body>

<h1 style="text-align: center;">500 Internal Server Error</h1>

<hr>

<p style="text-align: center;">HTTP-PyServer</p>

</body>

</html>''',
filetype='html',
code = response_codes.ResponseCodes.INTERNAL_SERVER_ERROR,
message = response_messages.ResponseMessages.INTERNAL_SERVER_ERROR)

    }

    def route(self,
              path: str,
              *,
              include_session: bool = False,
              static_ressources: dict[str: str] = None) -> callable:
        '''Adds a route to the server.
        
        :param path: The path to the route. Ex: '/home', '/about', '/contact'.
        :param include_session: Whether or not to include the session as a parameter.
        :param static_ressources: A dictionary of static ressources'''

        if static_ressources is None:

            static_ressources = {}

        for ressource_file_path, ressource_reference_path in static_ressources.items():

            ressource_reference_path = '/' + ressource_reference_path.strip('/')

            if pathlib.Path(ressource_file_path).exists():

                ressource = render.file(filepath = ressource_file_path)

                self._routes[ressource_reference_path] = \
                lambda _, ressource = ressource: ressource

        if include_session:

            self._session_routes.append(path.rstrip('/'))

        def callable_route(route_function):

            self._routes[path.rstrip('/')] = route_function

            return route_function
        
        return callable_route
    
    def root(self,
             *,
             include_session: bool = False) -> callable:
        
        self._root_uses_session = include_session

        def callable_root(route_function):

            self._root = route_function

            return route_function

        return callable_root
    
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

                if route in self._session_routes:

                    try:

                        if (self.sessions.exists(
                        session_id:=request.cookies().get('SESSION_ID'))):

                            session = self.sessions.get(session_id)

                        else:

                            session = self.sessions.get(self.sessions.add())

                    except Exception:

                        session = self.sessions.get(self.sessions.add())

                    if self._root:

                        if self._root_uses_session:

                            self._root(request, session)

                        else:
                        
                            self._root(request)

                    message = self._routes[path](request,
                                                 session,
                                                 *wildcard_values)
                    
                    if isinstance(message, str):

                        message = render.text(text = message)

                    if cookies:=message.headers.get('Set-Cookie'):

                        cookies += f', SESSION_ID={session.id}; \
Expires={session.expires}'

                        message.headers['Set-Cookie'] = cookies

                    else:

                        message.headers['Set-Cookie'] = f'SESSION_ID={session.id}; \
Expires={session.expires}'

                else:

                    if self._root:

                        if self._root_uses_session:

                            self._root(request, self.sessions.get(self.sessions.add()))

                        else:
                        
                            self._root(request)

                    message = self._routes[path](request,
                                                 *wildcard_values)

                    if isinstance(message, str):

                        message = render.text(text = message)

                if isinstance(message, response.Response):

                    return bytes(message)
                
                else:

                    raise TypeError(f'Expected function for {request.path} \
to return str, or Response, got {type(message)}.')

        return self._get_route(self._404route, request = request)

    def _get_route(self,
                  path: str,
                  *,
                  request: request.Request = request.Request()) -> bytes:
        '''Gets a route from the _routes dictionary.'''

        if path in self._routes:

            if path in self._session_routes:

                try:

                    if (self.sessions.exists(
                        session_id:=request.cookies().get('SESSION_ID'))):

                        session = self.sessions.get(session_id)

                    else:

                        session = self.sessions.get(self.sessions.add())

                except Exception:

                    session = self.sessions.get(self.sessions.add())

                if self._root:

                    if self._root_uses_session:

                        self._root(request, session)

                    else:
                    
                        self._root(request)

                message = self._routes[path](request,
                                             session)
                
                if isinstance(message, str):

                    message = render.text(text = message)

                if cookies:=message.headers.get('Set-Cookie'):

                    cookies += f', SESSION_ID={session.id}; Expires={session.expires}'

                    message.headers['Set-Cookie'] = cookies

                else:

                    message.headers['Set-Cookie'] = f'SESSION_ID={session.id}; \
Expires={session.expires}'

            else:
   
                if self._root:

                    if self._root_uses_session:

                        self._root(request, self.sessions.get(self.sessions.add()))

                    else:
                    
                        self._root(request)

                message = self._routes[path](request)

                if isinstance(message, str):

                    message = render.text(text = message)
            
            if isinstance(message, response.Response):

                return bytes(message)
            
            else:

                raise TypeError(f'Expected function for {request.path} \
to return str, or Response, got {type(message)}.')
            
        elif pathlib.Path(path).is_relative_to(
             pathlib.Path('/' + self._static_dir.as_posix().strip('/'))):

            return bytes(render.file(filepath = path.strip('/')))

        else:

            return self._get_wildcard_path(path = path,
                                          request = request)