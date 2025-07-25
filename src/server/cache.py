import threading
from typing import Any, Self

class Cache:
    '''Cache class for storing items.'''

    def __init__(self,
                 name: str,
                 reset_on_update: bool = False) -> None:
        '''Initializes the cache class.'''

        self._name = name

        self._reset_on_update = reset_on_update

        self._items = {}

    def add(self,
            item: 'CacheItem') -> None:
        '''Adds an item to the cache.
        If the item already exists, it is overwritten.'''

        item._parent = self

        if (old_item:=self._items.get(item.key)):

            if self._reset_on_update:

                old_item._timer.cancel()

                item._set_expire()

            self._items[item.key] = item

        else:

            self._items[item.key] = item

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
        
        if (item:=self._items.get(key)):
        
            return item.value
        
        return None
    
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

    def _set_expire(self) -> None:
        '''Sets the expiration timer.'''

        self._timer = threading.Timer(self._expire,
                            self._parent.remove,
                            args = (self.key,))
        
        self._timer.daemon = True

        self._timer.start()