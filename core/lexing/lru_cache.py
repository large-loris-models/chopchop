from collections import OrderedDict
from typing import Optional


class LRUCache[K, V]:
    """Copied from
    https://www.geeksforgeeks.org/python/lru-cache-in-python-using-ordereddict/"""
    # initialising capacity
    def __init__(self, capacity: int = 128):
        self.cache: OrderedDict[K, V] = OrderedDict()
        self.capacity: int = capacity

    def get(self, key: K) -> Optional[V]:
        if key not in self.cache:
            return None
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: K, value: V) -> None:
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
