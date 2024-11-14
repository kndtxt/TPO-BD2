#============ Imports ==================>

import redis
import pymongo
import json
from bson import ObjectId
from pydantic import ValidationError
from models import Cliente, Telefono
from functools import singledispatch        #provides method overloading among other things

#============ Dbs Connection ===========>

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = mongoClient["mydatabase"]    #Mongo only creates a db when it gets content
r = redis.Redis()

#============ Inserting Data ===========>
#r.mset({"Croatia": "Zagreb", "Bahamas":"Nassau", "Argentina":"Chuwut"})
#print(r.get("Argentina").decode("utf-8"))

#mydb = mongoClient["mydatabase"]
#mycol = mydb["customers"]
#print(mongoClient)
#print(mydb)
#print(mycol)

#============ Cache Methods ===========>
def remove_id_from_client(client_data):
    if isinstance(client_data, list):
        for item in client_data:
            remove_id_from_client(item)
    elif isinstance(client_data, dict):
        for key, value in client_data.items():
            if isinstance(value, ObjectId):
                client_data[key] = str(value)  # Convert ObjectId to string
            elif isinstance(value, dict) or isinstance(value, list):
                remove_id_from_client(value)  # Recursively handle nested dictionaries or lists
    return client_data

def cache_get(key):
    cached_data = r.get(key)
    if cached_data:
        try:
            result = json.loads(cached_data.decode('utf-8'))
            if isinstance(result, list):  # If it's a list, convert all `_id` fields
                for item in result:
                    if '_id' in item and isinstance(item['_id'], str):
                        item['_id'] = ObjectId(item['_id'])  # Convert string back to ObjectId
            elif isinstance(result, dict):  # For a single document
                if '_id' in result and isinstance(result['_id'], str):
                    result['_id'] = ObjectId(result['_id'])  # Convert string back to ObjectId
            return result
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    return None

def cache_set(key, data, ttl=3600):  # TTL 1 hora
    try:
        cleaned_data = remove_id_from_client(data)  # Clean the data (remove ObjectId)
        r.setex(key, ttl, json.dumps(cleaned_data))  # Convert Python dict/list to JSON string
    except Exception as e:
        print(f"Error serializing data: {e}")

#============ Clients ===========>
clients = mongoClient["DB2TPE"]["clients"]
clients.create_index([("nroCliente", pymongo.ASCENDING)], unique=True)

def insertClient(nroCliente, nombre, apellido, direccion, activo, codigoArea, nroTel, tipoTel):
    try:
        #nos fijamos si ya estaba cacheada la lista de esa combinación, de ser asi borramos para forzar q se actualice
        redis_key = f"clientes:{nombre}:{apellido}"
        cached_clients = cache_get(redis_key)
        if cached_clients:
            r.delete(redis_key)

        cliente = Cliente(
            nroCliente=nroCliente,
            nombre=nombre,
            apellido=apellido,
            direccion=direccion,
            activo=activo,
            telefono=Telefono(codigoArea=codigoArea, nroTel=nroTel, tipoTel=tipoTel)
        )  # chequea model
        cliente_dict = cliente.dict()

        newClient = clients.insert_one(cliente_dict)
        return newClient
    except ValidationError as e:
        print(f"Data validation error: {e}")
    except Exception as e:
        print(e)
        return None

@singledispatch
def getClient(*client):
    #estaria bueno cachear en redis aca pero no se como encontrarlo
    #si se cacheo con nrocli y te pasan nombe? por eso estoy cacheando en cada metodo
    raise NotImplementedError(f"Unsupported type: {type(client)}")

@getClient.register
def _(nroCliente: int):
    try:
        redis_key = f"cliente:{nroCliente}"
        cached_client = cache_get(redis_key)
        if cached_client:
            return cached_client 

        query = {"nroCliente": nroCliente}
        client = clients.find_one(query)

        if client:#cacheamos
            cache_set(redis_key, client)
            
        return client
    except Exception as e:
        print(f"Error finding client: {e}")
        return None

@getClient.register
def _(nombre: str, apellido: str):
    try:
        redis_key = f"clientes:{nombre}:{apellido}"
        cached_clients = cache_get(redis_key)
        if cached_clients:
            return cached_clients 

        query = {"nombre": nombre, "apellido": apellido}
        clients_list = list(clients.find(query))

        if clients_list:#cacheamos
            cache_set(redis_key, clients_list)
        return clients_list
    except Exception as e:
        print(f"Error finding client: {e}")
        return None


#============ Main ===========>
def main():
    insertClient(1, "John", "Doe", "Calle Falsa 123", True, 11, 12345678, "Celular")
    insertClient(2, "Jane", "Doe", "Calle Falsa 123", True, 11, 12345678, "Celular")
    print(getClient("Jane", "Doe"))
    print(getClient(1))

main()


