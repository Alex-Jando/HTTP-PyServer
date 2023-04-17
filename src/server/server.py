import threading
import socket
import sys
import logging

from . import request
from . import routes

def _handle_request(*args,
                    connection: socket.socket = None,
                    address: socket.AddressInfo = None) -> None:
    '''Handles a request from a client.'''
        
    try:

        raw_request = str()

        while True:

            raw_request += connection.recv(4096).decode(encoding = 'utf-8',
                                                        errors = 'ignore')

            if '\r\n\r\n' in raw_request or raw_request == '':

                break

        if not raw_request:

                logging.debug(f'Connection closed by client {address[0]}:{address[1]}.')

                connection.close()

                return None

        try:

            parsed_request = request.Request.from_string(address = address,
                                                         request = raw_request)

        except:

            logging.error(f'Invalid request from {address[0]}:{address[1]}, closing connection.')

            connection.close()

            return None

        if content_length:=parsed_request.headers.get('Content-Length'):

            if length_recieved:=len(raw_request.split('\r\n\r\n')[1]) < (length_to_recieve:=int(content_length)):

                raw_request += connection.recv(length_to_recieve - length_recieved).decode(encoding = 'utf-8',
                                                                                           errors = 'ignore')

                parsed_request = request.Request.from_string(address = address,
                                                             request = raw_request)

        logging.debug(f'Recieved {parsed_request.method.title()} request from {address[0]}:{address[1]} for {parsed_request.path if parsed_request.path else "/"}')

        connection.send(routes.Routes.get_route(path = parsed_request.path,
                                                request = parsed_request))

        logging.debug(f'Sent {parsed_request.method} response to {address[0]}:{address[1]} for {parsed_request.path if parsed_request.path else "/"}')

        connection.close()

    except Exception as e:

        logging.error(f'Error while handling request from {address[0]}:{address[1]}: "{e}".')

        try:
            
            connection.close()

        except:

            pass

        logging.debug(f'Connection closed with {address[0]}:{address[1]} by server.')

def _listen(*args,
           host: str = '127.0.0.1',
           port: int = '127.0.0.1') -> None:
    '''Listens for incoming connections and spawns a thread to handle each request.'''

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((host, port))

        s.listen()

        logging.info(f'Server hosted on {host}:{port}.')

        while True:

            connection, address = s.accept()

            threading.Thread(target = _handle_request,
                             kwargs = {'connection': connection, 'address': address},
                             daemon = True).start()

def run(*args,
        host: str = '127.0.0.1',
        port: int = 80,
        log: bool = False,
        logfile: str = '') -> None:
    '''Starts the server. If log is True, a log file will be created.'''
    
    if log:

        if logfile:

            logging.basicConfig(filename = logfile,
                                level = logging.NOTSET,
                                format = '%(levelname)s %(asctime)s in %(pathname)s %(funcName)s line %(lineno)d - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')

        else:

            logging.basicConfig(level = logging.NOTSET,
                                format = '%(levelname)s %(asctime)s in %(pathname)s %(funcName)s line %(lineno)d - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')

    threading.Thread(target = _listen,
                    kwargs = {'host': host, 'port': port},
                    daemon = True).start()

    while True:

        try:

            input('Press enter to exit...\n')

        except:

            pass

        logging.info('Exiting server...')
        sys.exit()