import mimetypes
import os

from . import response_codes
from . import request
from . import response
from . import routes
from . import response_messages

def _get_template(data: bytes,
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

def text(text: str,
         *,
         filetype: str = 'txt',
         code: int | response_codes.ResponseCodes = 200,
         message: str | response_messages.ResponseMessages = 'OK',
         ) -> response.Response:
    '''Returns a text response. Use this to return plain text, JSON, XML, etc.'''

    if type(code) == response_codes.ResponseCodes:

        code = code.value

    if type(message) == response_messages.ResponseMessages:

        message = message.value

    text = text.encode(encoding = 'utf-8',
                       errors = 'ignore')

    headers = {

        'Content-Type': mimetypes.guess_type(f'file.{filetype.strip(".")}')[0],

        'Content-Length': str(len(text)),

    }

    return response.Response(version = 1.1,
                             code = code,
                             message = message,
                             headers = headers,
                             body = text)

def file(filepath: str,
         *,
         request: request.Request = request.Request(),
         templated_vars: dict = {},
         code: int | response_codes.ResponseCodes = 200,
         message: str | response_messages.ResponseMessages = 'OK'
         ) -> response.Response:
    '''Returns a file as a response. Use this to return HTML, CSS, JS, images, etc.'''

    if type(code) == response_codes.ResponseCodes:

        code = code.value

    if type(message) == response_messages.ResponseMessages:

        message = message.value

    if not filepath or not os.path.exists(filepath):

        return routes.Routes.get_route('/404', request = request)
            
    else:

        with open(filepath, 'rb') as file:

            data = file.read()

    if templated_vars:

        data = _get_template(data = data,
                             **templated_vars)

    headers = {

        'Content-Type': mimetypes.guess_type(filepath)[0]\
                        or 'application/octet-stream',

        'Content-Length': str(len(data)),

    }

    return response.Response(version = 1.1,
                             code = code,
                             message = message,
                             headers = headers,
                             body = data)

def redirect(url: str) -> response.Response:
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

    return response.Response(version = 1.1,
                             code = response_codes.ResponseCodes.SEE_OTHER,
                             message = response_messages.ResponseMessages.SEE_OTHER,
                             headers = {'Location': url,
                                        'Content-Type': 'text/html',
                                        'Content-Length': str(len(redirect_request))},
                             body = redirect_request)

def attachment(filepath: str = '',
               *,
               is_download: bool = False,
               is_text: bool = False,
               filename: str = '',
               request: request.Request = request.Request()) -> response.Response:
    '''Returns a file as an attachment.
    Use this to return files for download or viewing.
    Sometimes browsers will preview text files, so you can use is_text
    to force the browser to display the raw text instead of previewing it.'''

    if not filepath or not os.path.exists(filepath):

        return routes.Routes.get_route('/404', request = request)

    with open(filepath, 'rb') as f:

        data = f.read()

    headers = {

        'Content-Type': 'text/plain' if is_text else\
                        mimetypes.guess_type(filepath)[0]\
                        or 'application/octet-stream',

        'Content-Length': str(len(data)),

        'Content-Disposition': ('attachment' if is_download else 'inline')\
                                + (f'; filename="{filename}"' if filename else '')

    }

    return response.Response(version = 1.1,
                             code = response_codes.ResponseCodes.OK,
                             message = response_messages.ResponseMessages.OK,
                             headers = headers,
                             body = data)