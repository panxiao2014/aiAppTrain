import json
import os
import asyncio
import aiofiles
from collections import OrderedDict
from datetime import datetime
from abc import ABC, abstractmethod
from utils.logUtil import setup_logger

logger = setup_logger("cacheUtil")


class CacheUtil:
    def __init__(self, max_size, cache_file, key_generator):
        """
        Initialize the news cache with configurable key generation.
        
        Args:
            max_size (int): Maximum number of cache entries
            cache_file (str): File to persist the cache to
            key_generator: Instance of KeyGenerator
        """
        self._lock = asyncio.Lock() 

        self.max_size = max_size
        self.cache_file = cache_file
        self.key_generator = key_generator

        self.cache = OrderedDict()  # Maintains insertion order for LRU
        return


    async def load_cache(self):
        """Load cache from file if it exists."""
        if not os.path.exists(self.cache_file):
            return
        
        async with self._lock:
            try:
                async with aiofiles.open(self.cache_file, mode='r') as f:
                    contents = await f.read()
                    data = json.loads(contents)
                    count = 0
                    for key, value in data.get('cache', {}).items():
                        self.cache[key] = value
                        count += 1

                    logger.info(f"Loaded {count} items from cache file {self.cache_file}")

            except (json.JSONDecodeError, IOError):
                logger.error(f"Failed to load cache from {self.cache_file}")
                self.cache = OrderedDict()
                return
        return


    async def _save_cache(self):
        """Save cache to file."""
        async with self._lock:
            try:
                async with aiofiles.open(self.cache_file, mode='w') as f:
                    await f.write(json.dumps({'cache': dict(self.cache)}))
            except IOError:
                logger.error(f"Failed to save cache to {self.cache_file}")
                return
        return
    

    async def get(self, *args, **kwargs):
        """
        Get item from cache using application-specific key generation.
        
        Args:
            *args: Positional arguments for key generation
            **kwargs: Keyword arguments for key generation
            
        Returns:
            str: Cached value if found, None otherwise
        """
        key = self.key_generator.generate_key(*args, **kwargs)
        async with self._lock:
            if key in self.cache:
                #use pop and reinsert it to the dict, so it will be regarded as recently used by putting it to the end of the dict:
                value = self.cache.pop(key)
                self.cache[key] = value


                return json.dumps(value)
        return None
    

    async def add(self, value, *args, **kwargs):
        """
        Add item to cache using application-specific key generation.
        
        Args:
            value: Value to cache (should be JSON-serializable)
            *args: Positional arguments for key generation
            **kwargs: Keyword arguments for key generation
        """
        key = self.key_generator.generate_key(*args, **kwargs)
        
        # If key exists, remove it first to update position
        async with self._lock:
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            self.cache[key] = value

        await self._save_cache()
        
        return
    

    # def clear(self):
    #     """Clear the cache and remove the persistence file."""
    #     self.cache.clear()
    #     try:
    #         os.remove(self.cache_file)
    #     except OSError:
    #         pass
    #     return
    


class KeyGenerator(ABC):
    """Abstract base class for cache key generators"""
    @abstractmethod
    def generate_key(self, *args, **kwargs):
        """Generate a cache key from the provided arguments"""
        pass

class StockNewsKeyGenerator(KeyGenerator):
    """Key generator for stock news application"""
    def generate_key(self, stock_symbol, days):
        #get the current date in format YYYY-MM-DD
        current_date = datetime.now().strftime("%Y-%m-%d")

        #key is stock_symbol:current_date:days
        return f"{stock_symbol}:{current_date}:{days}"