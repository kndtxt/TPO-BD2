#============ Imports ==================>

import redis
import json
from bson import ObjectId

#============ Dbs Connection ===========>
r = redis.Redis()

#============ Methods ===========>
def flushCache():
    r.flushdb()

#cause ObjetId is not JSON serializable
def remove_id_from_client(client_data):
    if isinstance(client_data, list):
        for item in client_data:
            remove_id_from_client(item)
    elif isinstance(client_data, dict):
        for key, value in client_data.items():
            if isinstance(value, ObjectId):
                client_data[key] = str(value)  # bye ObjectId to string
            elif isinstance(value, dict) or isinstance(value, list):
                remove_id_from_client(value)  
    return client_data

def cache_get(key):
    cached_data = r.get(key)
    if cached_data:
        try:
            result = json.loads(cached_data.decode('utf-8'))
            return result
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    return None

def cache_set(key, data):
    try:
        cleaned_data = remove_id_from_client(data)  # chau ObjectId
        r.set(key, json.dumps(cleaned_data))  # dict/list to JSON string
    except Exception as e:
        print(f"Error serializing data: {e}")

def cache_multiple_get(key):
    cached_keys = r.keys(key)
    if cached_keys:
        cached_data = r.mget(key)
        if cached_data:
            try:
                result = [json.loads(data.decode('utf-8')) for data in cached_data]
                return result
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
    return None

def cache_del(key):
    r.delete(key)