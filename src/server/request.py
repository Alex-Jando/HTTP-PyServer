import urllib
import json

class Request:
    '''Represents an HTTP request.'''

    def __init__(self,
                 *,
                 address: tuple = (),
                 method: str = '',
                 path: str = '',
                 version: float = '',
                 headers: dict = {},
                 body: str = '',
                 query: dict = {}):
        '''Initializes the request class.'''

        self.address: tuple[str, int] = address

        self.method: str = method

        self.path: str = path

        self.version: float = version

        self.headers: dict[str, str] = headers

        self.body: bytes = body

        self.query: dict[str, str] = query

    @classmethod
    def from_bytestring(cls,
                         *,
                         address: tuple = (),
                         request: bytes):
        '''Creates a request object from an HTTP request string.'''

        lines = request.split(b'\r\n')

        method, path, version = lines[0].decode(encoding = 'utf-8',
                                                errors = 'ignore').split(' ')

        if '?' in path:

            path, query = path.split('?')

        else:

            query = ''

        path = urllib.parse.unquote(path).rstrip('/')

        query = urllib.parse.parse_qs(query)

        for key, value in query.items():

            query[key] = value[0]

        headers = {}

        for line in lines[1:]:

            if line == b'':

                break

            key, value = line.decode(encoding = 'utf-8',
                                     errors = 'ignore').split(': ')

            headers[key] = value

        body = b'\r\n'.join(lines[lines.index(b'') + 1:])

        return cls(address = address,
                   method = method,
                   path = path,
                   version = float(version.split('/')[1]),
                   headers = headers,
                   body = body,
                   query = query)
    
    def __str__(self):
        '''Returns the request as an HTTP request string.'''

        return f'{self.method} {self.path if self.path else "/"} {self.version}\r\n' + \
'\r\n'.join([f'{key}: {value}' for key, value in self.headers.items()]) + \
'\r\n\r\n' + \
self.body.decode(encoding = 'utf-8',
                 errors = 'ignore')

    def cookies(self):
        '''Returns the request cookies as a dictionary.'''

        try:

            cookies = {}

            for cookie in self.headers.get('Cookie').split(';'):

                key, value = list(urllib.parse.parse_qs(cookie.strip()).items())[0]

                cookies[key] = value[0]

            return cookies
        
        except Exception as e:

            print(e)

            return {}

    def json(self):
        '''Returns the request body as a JSON object.'''

        return json.loads(self.body.decode(encoding = 'utf-8',
                                           errors = 'ignore'))
    
    def form(self):
        '''Returns the request body as parsed urlencoded form data.'''

        return urllib.parse.parse_qs(self.body.decode(encoding = 'utf-8',
                                                      errors = 'ignore'))
    
    def files(self):

        try:
        
            boundry = self.headers.get('Content-Type').split('; ')[1].split('=')[1]

            parts = self.body.split(b'--' + boundry.encode(encoding = 'utf-8',
                                    errors = 'ignore') + b'\r\n')[1:]
            
            parts[-1] = parts[-1].split(b'--' + boundry.encode(encoding = 'utf-8',
                                    errors = 'ignore') + b'--\r\n')[0]

        except Exception:

            return {}
        
        files = {}
        
        for part in parts:

            try:

                full_header, body = part.split(b'\r\n\r\n', 1)

                full_header = full_header.decode(encoding = 'utf-8',
                                                 errors = 'ignore').split('\r\n')

                headers = {name: value for name, value in 
                           [header.split(': ') for header in full_header]}
                
                if filename:=(
                   headers.get('Content-Disposition').split('=')[-1].strip('"')):

                    files[filename] = body

            except Exception:

                continue

        return files