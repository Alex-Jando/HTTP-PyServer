import mimetypes
import os

from . import responses
from . import request
from . import routes

def _get_template(*args,
                  data: bytes = '',
                  **template_vars) -> str:
    '''Replaces all template variables in a data with their values.
    Template variables are defined as {{var_name}},
    and are replaced with the value of var_name in template_vars.'''
    
    for var_name, var_value in template_vars.items():

        data = data.replace(f'{{{{{var_name}}}}}'.encode(encoding = 'utf-8',
                                                         errors = 'ignore'),
                            var_value.encode(encoding = 'utf-8',
                                             errors = 'ignore'))

    return data

def text(*args,
         text: str = '',
         filetype: str = 'txt',
         code: int | responses.ResponseCodes = 200,
         message: str | responses.ResponseMessages = 'OK',
         ) -> bytes:
    '''Returns a text response. Use this to return plain text, JSON, XML, etc.'''

    text = text.encode(encoding = 'utf-8',
                       errors = 'ignore')

    headers = {

        'Content-Type': mimetypes.guess_type(f'file.{filetype.strip(".")}')[0],

        'Content-Length': str(len(text)),

    }

    return (f'HTTP/1.1 {code} {message}\r\n'\
            + '\r\n'.join([f'{key}: {value}' for key, value in headers.items()])) \
            .encode(encoding = 'utf-8',
            errors = 'ignore') \
            + b'\r\n\r\n' \
            + text

def file(*args,
         filepath: str = '',
         request: request.Request = request.Request(),
         templated_vars: dict = {},
         code: int | responses.ResponseCodes = 200,
         message: str | responses.ResponseMessages = 'OK'
         ) -> bytes:
    '''Returns a file as a response. Use this to return HTML, CSS, JS, images, etc.'''

    if not filepath or not os.path.exists(filepath):

        return text(text = routes.Routes.get_route('/404',
                                                   request = request),
                    code = responses.ResponseCodes.NOT_FOUND,
                    message = responses.ResponseMessages.NOT_FOUND)
            
    else:

        with open(filepath, 'rb') as file:

            data = file.read()

    if templated_vars:

        data = _get_template(data = data,
                             **templated_vars)

    headers = {

        'Content-Type': mimetypes.guess_type(os.path.basename(filepath))[0]\
                        or 'application/octet-stream',

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

    return redirect_request.encode(encoding = 'utf-8',
                                   errors = 'ignore')

def attachment(*args,
               filepath: str = '',
               is_download: bool = False,
               is_text: bool = False,
               filename: str = '',
               request: request.Request = request.Request()) -> bytes:
    '''Returns a file as an attachment.
    Use this to return files for download or viewing.
    Sometimes browsers will preview text files, so you can use is_text
    to force the browser to display the raw text instead of previewing it.'''

    if not filepath or not os.path.exists(filepath):

        return text(text = routes.Routes.get_route('/404',
                                                   request = request),
                    code = responses.ResponseCodes.NOT_FOUND,
                    message = responses.ResponseMessages.NOT_FOUND)

    with open(filepath, 'rb') as f:

        data = f.read()

    headers = {

        'Content-Type': 'text/plain' if is_text else\
                        mimetypes.guess_type(os.path.basename(filepath))[0]\
                        or 'application/octet-stream',

        'Content-Length': str(len(data)),

        'Content-Disposition': ('attachment' if is_download else 'inline')\
                                + f'; filename="{filename}"' if filename else ''

    }

    return ('HTTP/1.1 200 OK\r\n' \
            + '\r\n'.join([f'{key}: {value}' for key, value in headers.items()])) \
            .encode(encoding = 'utf-8',
            errors = 'ignore') \
            + b'\r\n\r\n' \
            + data