import threading
import socket
import logging
from typing import Self

from . import request
from . import routes

class Server(routes.Routes):
    '''HTTP server running on a specified host and port.'''

    def __init__(self,
                 *,
                 host: str = '127.0.0.1',
                 port: int = 80,
                 logger: logging.Logger = None) -> None:
        '''Initializes the server class.'''
        
        super().__init__()
        
        self._host: str = host

        self._port: int = port

        self._logger: logging.Logger = logger

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self) -> None:
        '''Starts the server.'''
        
        threading.Thread(target = self._listen,
                         daemon = True).start()
        
    def wait(self) -> None:
        '''Waits for Enter key press or KeyboardInterrupt.'''

        try:

            input('Press Enter to continue...\n')

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

        self._socket.bind((self._host, self._port))

        self._socket.listen()

        if self._logger:

            self._logger.info(f'Server hosted on {self._host}:{self._port}.')
            
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

                raw_request = ''

                while True:

                    raw_request += connection.recv(4096).decode(encoding = 'utf-8',
                                                                errors = 'ignore')

                    if '\r\n\r\n' in raw_request or raw_request == '':

                        break

                if not raw_request:
                        
                        if self._logger:

                            self._logger.debug(f'Connection closed by client \
{address[0]}:{address[1]}.')

                        connection.close()

                        return None

                try:

                    parsed_request = request.Request.from_string(address = address,
                                                                 request = raw_request)

                except Exception:

                    if self._logger:

                        self._logger.error(f'Invalid request from \
{address[0]}:{address[1]}, closing connection.')

                    connection.close()

                    return None

                if content_length:=parsed_request.headers.get('Content-Length'):

                    if length_recieved:=len(raw_request.split('\r\n\r\n')[1]) < \
                    (length_to_recieve:=int(content_length)):

                        raw_request += connection.recv(length_to_recieve - \
                                                       length_recieved)\
                            .decode(encoding = 'utf-8',
                                    errors = 'ignore')

                        parsed_request = request.Request.from_string(address = address,
                                                                request = raw_request)
                        
                if self._logger:

                    self._logger.debug(f'Recieved request from \
{address[0]}:{address[1]} for {parsed_request.path if parsed_request.path else "/"}')

                connection.send(self._get_route(path = parsed_request.path,
                                                request = parsed_request))
                
                if self._logger:

                    self._logger.debug(f'Sent {parsed_request.method} response to \
{address[0]}:{address[1]} for {parsed_request.path if parsed_request.path else "/"}')

                if not parsed_request.headers.get('Connection') == 'keep-alive':

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
{address[0]}:{address[1]}: "{e}".')                

                return None

    def __enter__(self) -> Self:
        '''Starts the server.'''

        self.start()

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        '''Stops the server.'''

        self.stop()