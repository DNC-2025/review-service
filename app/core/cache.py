from cachetools import TTLCache
from typing import Any

# Cache globale: massimo 100 voci, TTL 60 secondi
cache = TTLCache(maxsize=100, ttl=60)

def make_cache_key(*args, **kwargs) -> str:
    """
    Genera una chiave unica per la cache basata su parametri della query.
    """
    key_parts = [str(arg) for arg in args]
    key_parts += [f"{k}={v}" for k, v in sorted(kwargs.items())]
    return "|".join(key_parts)

def get_from_cache(key: str) -> Any:
    return cache.get(key)

def set_in_cache(key: str, value: Any):
    cache[key] = value
