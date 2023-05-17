import secrets
import threading
import time
from typing import Any

class Session:
     
    def __init__(self,
                session_id: str) -> None:
        '''Initializes the session class.'''
        
        self._session_id: str = session_id
        
        self._items: dict[str, Any] = {}

    @property
    def id(self) -> str:
        '''Returns the session id.'''
        
        return self._session_id
    
    def set(self,
            key: str,
            value: Any) -> None:
        '''Adds an item to the session.
        If the item already exists, it is overwritten.'''
        
        self._items[key] = value

    def remove(self,
               key: str) -> None:
         
        '''Removes an item from the session.'''

        self._items.pop(key)

    def get(self,
            key: str) -> Any:
         
        '''Gets an item from the session. Returns "None" if the item does not exist.'''

        return self._items.get(key)
    
    def update(self) -> None: 
        '''Updates the session id, and resets the timer.'''

        self._parent.remove(self._session_id)

        while self._parent._session.get(session_id := secrets.token_urlsafe(128)):
             pass
        
        self._session_id = session_id

        self._parent._sessions[self._session_id] = self

        remove_timer = threading.Timer(self._parent._remove_after,
                                       self._parent.remove,
                                       args = (self._session_id,))

        self._parent._remove_dict[self._session_id] = remove_timer

        remove_timer.start()

    @property
    def expires(self) -> str:
        '''Returns the expires in header format.'''

        return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(self._expires))

class Sessions:

    def __init__(self,
                 remove_after: float = 900) -> None:
        '''Sessions class for storing sessions.
        :param remove_after: The time in seconds after which a session is removed.'''
        
        self._sessions: dict[str, Session] = {}

        self._remove_dict: dict[str, threading.Timer] = {}

        self._remove_after: float = remove_after

    def add(self) -> None:
        '''Adds a session to the sessions.'''

        while self._sessions.get(session_id := secrets.token_urlsafe(128)):
            pass

        self._sessions[session_id] = Session(session_id)

        self._sessions[session_id]._parent = self

        remove_timer: threading.Timer = threading.Timer(self._remove_after,
                        self.remove,
                        args = (session_id,))
        
        self._remove_dict[session_id] = remove_timer

        remove_timer.start()

        self._sessions[session_id]._expires = time.time() + self._remove_after

        return session_id

    def remove(self,
               session_id: str) -> None:
          '''Removes a session from the sessions.'''
    
          try:
                
                self._remove_dict.pop(session_id).cancel()
    
                self._sessions.pop(session_id)
    
          except Exception:
    
                pass
          
    def exists(self,
               session_id: str) -> bool:
          '''Checks if a session exists.'''
    
          return session_id in self._sessions
    
    def get(self,
            session_id: str) -> Session:
          '''Gets a session from the sessions.'''
    
          return self._sessions.get(session_id)