import mimetypes
import pathlib

from . import response_codes
from . import response
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
         headers: dict = None) -> response.Response:
    '''Returns a text response. Use this to return plain text, JSON, XML, etc.'''

    if not headers:

        headers = {}

    if type(code) == response_codes.ResponseCodes:

        code = code.value

    if type(message) == response_messages.ResponseMessages:

        message = message.value

    text = text.encode(encoding = 'utf-8',
                       errors = 'ignore')
    
    headers['Content-Length'] = str(len(text))

    headers['Content-Type'] = mimetypes.guess_type(f'file.{filetype.strip(".")}')[0]\
                              or 'text/plain'

    return response.Response(version = 1.1,
                             code = code,
                             message = message,
                             headers = headers,
                             body = text)

def file(filepath: str,
         *,
         templated_vars: dict = {},
         code: int | response_codes.ResponseCodes = 200,
         message: str | response_messages.ResponseMessages = 'OK',
         headers: dict = None
         ) -> response.Response:
    '''Returns a file as a response. Use this to return HTML, CSS, JS, images, etc.'''

    if not headers:

        headers = {}

    if type(code) == response_codes.ResponseCodes:

        code = code.value

    if type(message) == response_messages.ResponseMessages:

        message = message.value

    if not filepath or not pathlib.Path(filepath).exists():

        raise FileNotFoundError(f'File not found: {filepath}')
            
    else:

        with open(filepath, 'rb') as file:

            data = file.read()

    if templated_vars:

        data = _get_template(data = data,
                             **templated_vars)

    headers['Content-Length'] = str(len(data))
    headers['Content-Type'] = mimetypes.guess_type(filepath)[0]\
                              or 'application/octet-stream'

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
               filename: str = '',
               headers: dict = None) -> response.Response:
    '''Returns a file as an attachment.
    Use this to return files for download or viewing.
    Sometimes browsers will preview text files, so you can use is_text
    to force the browser to display the raw text instead of previewing it.'''

    if not headers:

        headers = {}

    if not filepath or not pathlib.Path(filepath).exists():

        raise FileNotFoundError(f'File not found: {filepath}')

    with open(filepath, 'rb') as f:

        data = f.read()

    headers['Content-Length'] = str(len(data))
    headers['Content-Type'] = mimetypes.guess_type(filepath)[0]\
                              or 'application/octet-stream'
    headers['Content-Disposition'] = ('attachment' if is_download else 'inline')\
                                     + (f'; filename="{filename}"' if filename else '')

    return response.Response(version = 1.1,
                             code = response_codes.ResponseCodes.OK,
                             message = response_messages.ResponseMessages.OK,
                             headers = headers,
                             body = data)