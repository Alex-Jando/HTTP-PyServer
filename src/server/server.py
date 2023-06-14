import threading
import socket
import logging
from typing import Self
import ssl
import pathlib

from . import request
from . import routes
from . import sessions

class Server(routes.Routes):
    '''HTTP server running on a specified host and port.'''

    def __init__(self,
                 *,
                 host: str = '127.0.0.1',
                 port: int = 80,
                 logger: logging.Logger = None,
                 _404route: str = '/404',
                 _500route: str = '/500',
                 static_dir: str = 'static/',
                 ssl_context: ssl.SSLContext = None,
                 sessions_expire_after: float = 900) -> None:
        '''Initializes the server class.
        
        :param host: The IP address to run the server on.
        :param port: The port to run the server on.
        :param logger: The logger to use for logging.
        :param _404route: The route to use for 404 errors.
        :param _500route: The route to use for 500 errors.
        :param static_dir: The directory to use for static files.
        :param ssl_context: The SSL context to use for HTTPS.'''
        
        self._host: str = host

        self._port: int = port

        self._logger: logging.Logger = logger

        self._404route: str = _404route

        self._500route: str = _500route

        self._static_dir: pathlib.Path = pathlib.Path(static_dir.strip('/'))

        if not self._static_dir.exists():

            if self._logger:

                self._logger.warning(f'Static directory "{static_dir}" does not exist.')

        self._ssl_context: ssl.SSLContext = ssl_context

        self.sessions: sessions.Sessions = \
        sessions.Sessions(remove_after = sessions_expire_after)

        super().__init__()

    def start(self) -> None:
        '''Starts the server.'''

        if self._logger:

            self._logger.info('Starting server...')
        
        threading.Thread(target = self._listen,
                        daemon = True).start()
        
    def wait(self,
             msg: str = '') -> None:
        '''Waits for Enter key press or KeyboardInterrupt.'''

        try:

            input(msg + '\n' if msg else '')

        except (KeyboardInterrupt, EOFError):

            pass

    def stop(self) -> None:
        '''Stops the server.'''

        if self._logger:

            self._logger.info('Stopping server...')

        self._socket.close()

        if self._logger:

            self._logger.info('Server stopped.')

    def _listen(self) -> None:
        '''Listens for incoming connections 
        and spawns a thread to handle each request.'''

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if self._ssl_context:

            self._socket = self._ssl_context.wrap_socket(self._socket,
                                                         server_side = True)

        self._socket.bind((self._host, self._port))

        self._socket.listen()

        if self._logger:

            self._logger.info(f'Server hosted on http{"s" if self._ssl_context else ""}\
://{self._host}:{self._port}.')
            
        while True:

            try:

                connection, address = self._socket.accept()

                threading.Thread(target = self._handle_request,
                                kwargs = {'connection': connection,
                                        'address': address},
                                daemon = True).start()

            except OSError:

                break
                
    def _handle_request(self,
                        connection: socket.socket,
                        address: socket.AddressInfo) -> None:
        '''Handles a request from a client.'''

        while True:
            
            try:

                raw_request = b''

                while True:

                    raw_request += connection.recv(4096)

                    if b'\r\n\r\n' in raw_request or raw_request == b'':

                        break

                if not raw_request:
                        
                    if self._logger:

                        self._logger.debug(f'Connection closed by client \
{address[0]}:{address[1]}.')

                    connection.close()

                    return None

                try:

                    parsed_request = request.Request.from_bytestring(address = address,
                                     request = raw_request)

                except Exception:

                    if self._logger:

                        self._logger.error(f'Invalid request from \
{address[0]}:{address[1]}, closing connection.')

                    connection.close()

                    return None

                if content_length:=(parsed_request.headers.get('Content-Length') or \
                                    parsed_request.headers.get('content-length')):

                    content_length = int(content_length)
                        
                    while (body_length:=len(raw_request.split(b'\r\n\r\n', 1)[1]))\
                    < (content_length):

                        raw_request += connection.recv(content_length - body_length)

                    parsed_request = request.Request.from_bytestring(
                                    address = address,
                                    request = raw_request)

                if self._logger:

                    self._logger.debug(f'Recieved {parsed_request.method} request from \
{address[0]}:{address[1]} for {parsed_request.path if parsed_request.path else "/"}')

                connection.send(self._get_route(path = parsed_request.path,
                                                request = parsed_request))
                
                if self._logger:

                    self._logger.debug(f'Sent {parsed_request.method} response to \
{address[0]}:{address[1]} for {parsed_request.path if parsed_request.path else "/"}')

                if not (parsed_request.headers.get('Connection') or \
                        parsed_request.headers.get('connection')) == 'keep-alive':

                    try:
                
                        connection.close()

                    except Exception:

                        pass

                    if self._logger:

                        self._logger.debug(f'Connection closed with \
{address[0]}:{address[1]} by client.')

                    return None

            except Exception as e:

                if self._logger:

                    self._logger.error(f'Error while handling request from \
{address[0]}:{address[1]} : "{e}".') 

                try:

                    connection.send(self._get_route(path = self._500route,
                                                    request = parsed_request))
                    
                    connection.close()

                except Exception:

                    pass

                return None

    def __enter__(self) -> Self:
        '''Starts the server.'''

        self.start()

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        '''Stops the server.'''

        self.stop()