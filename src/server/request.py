import urllib

class Request:

    def __init__(self,
                 *args,
                 method: str = '',
                 path: str = '',
                 version: str = '',
                 headers: dict = {},
                 body: str = '',
                 query: dict = {},
                 values: dict = {}):
        '''Initializes the request class.'''

        self.method = method

        self.path = path

        self.version = version

        self.headers = headers

        self.body = body

        self.query = query

        self.values = values

    @classmethod
    def from_string(cls,
                    *args,
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

        headers = dict()

        for line in lines[1:]:

            if line == '':

                break

            key, value = line.split(': ')

            headers[key] = value

        body = '\r\n'.join(lines[lines.index('') + 1:])

        if method == 'POST':

            values = dict()

            for key, value in urllib.parse.parse_qs(body).items():

                values[key] = value[0]

            return cls(method = method,
                       path = path,
                       version = version,
                       headers = headers,
                       body = body,
                       query = query,
                       values = values)

        return cls(method = method,
                   path = path,
                   version = version,
                   headers = headers,
                   body = body,
                   query = query)