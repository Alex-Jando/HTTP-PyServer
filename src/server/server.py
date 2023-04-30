import threading
import socket
import sys
import logging

from . import request
from . import routes

def _handle_request(*,
                    connection: socket.socket = None,
                    address: socket.AddressInfo = None,
                    logger: logging.Logger = None) -> None:
    '''Handles a request from a client.'''

    while True:
        
        try:

            raw_request = str()

            while True:

                raw_request += connection.recv(4096).decode(encoding = 'utf-8',
                                                            errors = 'ignore')

                if '\r\n\r\n' in raw_request or raw_request == '':

                    break

            if not raw_request:
                    
                    if logger:

                        logger.debug(f'Connection closed by client \
{address[0]}:{address[1]}.')

                    connection.close()

                    return None

            try:

                parsed_request = request.Request.from_string(address = address,
                                                            request = raw_request)

            except Exception:

                if logger:

                    logger.error(f'Invalid request from {address[0]}:{address[1]}, \
closing connection.')

                connection.close()

                return None

            if content_length:=parsed_request.headers.get('Content-Length'):

                if length_recieved:=len(raw_request.split('\r\n\r\n')[1]) < \
                (length_to_recieve:=int(content_length)):

                    raw_request += connection.recv(length_to_recieve - length_recieved)\
                        .decode(encoding = 'utf-8',
                                errors = 'ignore')

                    parsed_request = request.Request.from_string(address = address,
                                                                request = raw_request)
                    
            if logger:

                logger.debug(f'Recieved {parsed_request.method.title()} request from \
{address[0]}:{address[1]} for \
{parsed_request.path if parsed_request.path else "/"}')
                
            message = routes.Routes.get_route(path = parsed_request.path,
                                              request = parsed_request)

            connection.send(message)
            
            if logger:

                logger.debug(f'Sent {parsed_request.method} response to \
{address[0]}:{address[1]} for {parsed_request.path if parsed_request.path else "/"}')
                
            if not parsed_request.headers.get('Connection') == 'keep-alive':

                try:
            
                    connection.close()

                except Exception:

                    pass

                if logger:

                    logger.debug(f'Connection closed with \
{address[0]}:{address[1]} by server.')

                return None

        except Exception as e:

            if logger:

                logger.error(f'Error while handling request from \
{address[0]}:{address[1]}: "{e}".')
                

            return None

def _listen(*,
           host: str = '127.0.0.1',
           port: int = '127.0.0.1',
           logger: logging.Logger = None) -> None:
    '''Listens for incoming connections and spawns a thread to handle each request.'''

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((host, port))

        s.listen()

        if logger:

            logger.debug(f'Server hosted on {host}:{port}.')

        while True:

            connection, address = s.accept()

            threading.Thread(target = _handle_request,
                             kwargs = {'connection': connection,
                                       'address': address,
                                       'logger': logger},
                             daemon = True).start()

def run(*,
        host: str = '127.0.0.1',
        port: int = 80,
        logger: logging.Logger = None) -> None:
    '''Starts the server. Specify the HOST and PORT to listen on.
    Optionally, specify a logging.Logger object to log to.'''  

    threading.Thread(target = _listen,
                    kwargs = {'host': host,
                              'port': port,
                              'logger': logger},
                    daemon = True).start()

    try:

        input('Press Enter to continue...\n')

    except (KeyboardInterrupt, EOFError):

        pass

    if logger:

        logger.info('Exiting server...')

    sys.exit()