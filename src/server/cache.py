import threading
from typing import Any, Self

class Cache:
    '''Cache class for storing items.'''

    def __init__(self,
                 name: str):
        '''Initializes the cache class.'''

        self._name = name

        self._items = {}

    def add(self,
            item: 'CacheItem') -> None:
        '''Adds an item to the cache.
        If the item already exists, it is overwritten.'''
        
        item._set_parent(self)

        self._items[item.key] = item.value

        item._set_expire()

    def remove(self,
               key: str) -> None:
        '''Removes an item from the cache.
        If the item does not exist, nothing happens.'''
        
        try:
        
            self._items.pop(key)

        except KeyError:

            pass

    def get(self,
            key: str) -> Any:
        '''Gets value of an item from the cache.
        If the value of the item does not exist, returns None.'''
        
        return self._items.get(key)
    
    def __getitem__(self,
                    key: str) -> Any:
        '''Gets an item from the cache.
        If the item does not exist, returns None.'''
        
        return self.get(key)
    
    def __iadd__(self,
                 item: 'CacheItem') -> Self:
        '''Adds an item to the cache.
        If the item already exists, it is overwritten.'''
        
        self.add(item)

        return self
    
    def __isub__(self,
                 key: str) -> Self:
        '''Removes an item from the cache.
        If the item does not exist, nothing happens.'''
        
        self.remove(key)

        return self

class CacheItem:
    '''Cache item class for storing items.'''

    def __init__(self,
                 key: str,
                 value: Any,
                 expire: int | float = 0) -> None:
        '''Initializes the cache item class. expire is in seconds.
        If expire is 0, the item never expires.'''

        self.key = key
        self.value = value
        self._expire = expire

    def _set_parent(self,
                    parent: Cache) -> None:
        '''Sets the parent cache.'''

        self._parent = parent

    def _set_expire(self) -> None:
        '''Sets the expiration timer.'''

        t = threading.Timer(self._expire,
                            self._parent.remove,
                            args = (self.key,))
        
        t.daemon = True

        t.start()