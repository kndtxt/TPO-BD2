#============ Imports ==================>

import redis
import json
from datetime import datetime
from bson import ObjectId, json_util

#============ Dbs Connection ===========>
r = redis.Redis()

#============ Methods ===========>
def flushCache():
    r.flushdb()

def cache_get(key):
    cached_data = r.get(key)
    if cached_data:
        try:
            result = json.loads(cached_data)
            return result
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    return None

def cache_set(key, data, ttl=3600):  # TTL 1 hora
    try:
        r.setex(key, ttl, json.dumps(data, default=str))  # dict/list to JSON string
    except Exception as e:
        print(f"Error serializing data: {e}")

def cache_del(key):
    r.delete(key)