#============ Imports ==================>

import redis
import json
from bson import ObjectId

#============ Dbs Connection ===========>
r = redis.Redis()

#============ Methods ===========>
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
            if isinstance(result, list):
                for item in result:
                    if '_id' in item and isinstance(item['_id'], str):
                        item['_id'] = ObjectId(item['_id'])  # welcome back to ObjectId
            elif isinstance(result, dict):  # For a single document
                if '_id' in result and isinstance(result['_id'], str):
                    result['_id'] = ObjectId(result['_id'])  # welcome back to ObjectId
            return result
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    return None

def cache_set(key, data, ttl=3600):  # TTL 1 hora
    try:
        cleaned_data = remove_id_from_client(data)  # chau ObjectId
        r.setex(key, ttl, json.dumps(cleaned_data))  # dict/list to JSON string
    except Exception as e:
        print(f"Error serializing data: {e}")

def cache_del(key):
    r.delete(key)