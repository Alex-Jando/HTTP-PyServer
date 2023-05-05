from . import response_codes
from . import response_messages

class Response:
    '''Represents an HTTP response.'''

    def __init__(self,
                 version: float,
                 code: int | response_codes.ResponseCodes,
                 message: str | response_messages.ResponseMessages,
                 headers: dict,
                 body: str | bytes = ''):
        '''Initializes the response class.'''

        self.version: float = version

        if isinstance(code, response_codes.ResponseCodes):
            
            code = code.value

        if isinstance(message, response_messages.ResponseMessages):
            
            message = message.value

        self.code: int | response_codes.ResponseCodes = code

        self.message: str | response_messages.ResponseMessages = message

        self.headers: dict = headers

        self.body: str | bytes = body

    def __str__(self):
        '''Returns the response as a string.
        This is not a valid HTTP response as the body is not encoded.'''

        return f'HTTP/{self.version} {self.code} {self.message}\r\n' \
+ '\r\n'.join([f'{key}: {value}' for key, value in self.headers.items()]) \
+ '\r\n\r\n' \
+ (self.body if isinstance(self.body, str) else self.body.decode(encoding = 'utf-8',
                                                                errors = 'ignore'))

    def __bytes__(self):
        '''Returns the response as a bytes object. This is a valid HTTP response.'''

        return (f'HTTP/{self.version} {self.code} {self.message}\r\n'\
+ '\r\n'.join([f'{key}: {value}' for key, value in self.headers.items()]) + '\r\n\r\n')\
.encode(encoding = 'utf-8',
        errors = 'ignore')\
+ (self.body if isinstance(self.body, bytes) else self.body.encode(encoding = 'utf-8',
                                                                  errors = 'ignore'))
    
    def __repr__(self):
        '''Returns representation of the response as a string.'''

        return f'<Response(version = {self.version}, \
code = {self.code}, \
message = {self.message})>'