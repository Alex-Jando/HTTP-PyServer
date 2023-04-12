import mimetypes
import os
import urllib

from . import request
from . import routes

def _get_template(*args,
                  data: bytes = '',
                  **template_vars) -> str:
    '''Replaces all template variables in a data with their values. Template variables are defined as {{var_name}}, and are replaced with the value of var_name in template_vars.'''
    
    if not data:
        
        return ''
    
    for var_name, var_value in template_vars.items():

        data = data.replace(f'{{{{{var_name}}}}}', str(var_value))

    return data

def file(*args,
         data: str = '',
         filepath: str = '',
         extension: str = '',
         request: request.Request = None,
         templated_vars: dict = {},
         code: int = 200,
         message: str = 'OK'
         ) -> bytes:
    '''Returns a file as a response. Use this to return HTML, CSS, JS, images, etc.'''

    if filepath:

        if not os.path.exists(filepath):

            data = routes.Routes.get_route(path = '404',
                                           request = request)
            
        else:

            with open(filepath, 'r') as file:

                data = file.read()

    if templated_vars:

        data = _get_template(data = data,
                             **templated_vars)

    data = data.encode(encoding = 'utf-8',
                        errors = 'ignore')

    headers = {

        'Content-Type': mimetypes.guess_type(f'file.{extension.strip(".")}')[0] or mimetypes.guess_type(os.path.basename(filepath))[0] or 'text/plain',

        'Content-Length': str(len(data)),

    }

    return (f'HTTP/1.1 {code} {message}\r\n' \
            + '\r\n'.join([f'{key}: {value}' for key, value in headers.items()])) \
            .encode(encoding = 'utf-8',
            errors = 'ignore') \
            + b'\r\n\r\n' \
            + data

def redirect(*args,
             url: str = '') -> bytes:
    '''Returns a redirect request to the specified URL.'''

    redirect_request = f'HTTP/1.1 301 See Other\
        \r\nLocation: {url}\
        \r\nContent-Type: text/html\
        \r\n\r\n\
        <html>\
            <head>\
                <meta http-equiv="refresh" content="0;URL={url}" />\
            </head>\
        </html>'
    
    print(len(redirect_request))

    print(len('<html>\
            <head>\
                <meta http-equiv="refresh" content="0;URL=" />\
            </head>\
        </html>'))

    return redirect_request.encode(encoding = 'utf-8',
                                   errors = 'ignore')

def attachment(*args,
               filepath: str = '',
               filedata: bytes = b'',
               download: bool = False,
               text: bool = False,
               filename: str = '',
               request: request.Request = None) -> bytes:
    '''Returns a file as an attachment. Can be used to download or view files.'''

    if not filepath:

        data = filedata

    elif not os.path.exists(filepath): # Filepath entered does not exist

        return file(data = routes.Routes.get_route(path = '404',
                                            request = request),
                    code = 404,
                    message = 'Not Found'
                    )
    
    else:

        with open(filepath, 'rb') as file:

            data = file.read()

    headers = {

        'Content-Type': 'text/plain' if text else mimetypes.guess_type(os.path.basename(filepath))[0] or 'application/octet-stream',

        'Content-Length': str(len(data)),

        'Content-Disposition': ('attachment' if download else 'inline') + f'; filename="{urllib.parse.quote(filename)}"' if filename else ('attachment' if download else 'inline')

    }

    return (f'HTTP/1.1 200 OK\r\n' \
            + '\r\n'.join([f'{key}: {value}' for key, value in headers.items()])) \
            .encode(encoding = 'utf-8',
            errors = 'ignore') \
            + b'\r\n\r\n' \
            + data