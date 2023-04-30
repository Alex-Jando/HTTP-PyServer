import urllib
import json

class Request:
    '''Represents an HTTP request.'''

    def __init__(self,
                 *,
                 address: tuple = (),
                 method: str = '',
                 path: str = '',
                 version: str = '',
                 headers: dict = {},
                 body: str = '',
                 query: dict = {}):
        '''Initializes the request class.'''

        self.address = address

        self.method = method

        self.path = path

        self.version = version

        self.headers = headers

        self.body = body

        self.query = query

    @classmethod
    def from_string(cls,
                    *args,
                    address: tuple = (),
                    request: str):
        '''Creates a request object from an HTTP request string.'''

        lines = request.split('\r\n')

        method, path, version = lines[0].split(' ')

        path = urllib.parse.unquote(path).replace('\\', '/')

        if '?' in path:

            path, query = path.split('?')

        else:

            query = {}

        path = path.rstrip('/')

        query = urllib.parse.parse_qs(query)

        for key, value in query.items():

            query[key] = value[0]

        headers = {}

        for line in lines[1:]:

            if line == '':

                break

            key, value = line.split(': ')

            headers[key] = value

        body = '\r\n'.join(lines[lines.index('') + 1:])

        return cls(address = address,
                   method = method,
                   path = path,
                   version = version,
                   headers = headers,
                   body = body,
                   query = query)
    
    def __str__(self):
        '''Returns the request as an HTTP request string.'''

        return f'{self.method} {self.path} {self.version}\r\n' + \
'\r\n'.join([f'{key}: {value}' for key, value in self.headers.items()]) + \
'\r\n\r\n' + \
self.body

    def json(self):
        '''Returns the request body as a JSON object.'''

        return json.loads(self.body)
    
    def form(self):
        '''Returns the request body as parsed urlencoded form data.'''

        return urllib.parse.parse_qs(self.body)