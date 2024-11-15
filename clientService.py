#============ Imports ==================>
from persistence import mydb, mongoClient, CLIENTS
from productService import getProduct
import cache as c
from models import Client
from pydantic import ValidationError
from functools import singledispatch
from pymongo.errors import DuplicateKeyError

#============ Setters ==================>
def insertClient(client):
    """
    Inserts client into database.

    Args:
        client dictionary, according the Client model

    Returns:
        client if created. None otherwise.
    """ 
    try:
        redis_key = f"clients:{client['nombre']}:{client['apellido']}"#forced delete id cached in redis
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            c.cache_del(redis_key)

        aux_client = Client(**client)#validate by model
        newClient = CLIENTS.insert_one(aux_client.dict())
        return newClient

    except ValidationError as e:
        print(f"Data validation error: {e}")
    except DuplicateKeyError as e:
        print(f"Client for nroCliente: {client['clientNbr']} already exists!")
        return None
    except Exception as e:
        print(e)
        return None

#============ Getters ===========>
@singledispatch
def getClient(*client):
    raise NotImplementedError(f"Unsupported type: {type(client)}")

@getClient.register
def _(clientNbr: int):
    """
    Searches for the client with the given clientNbr in database.
    Uses redis caching.

    Args:
        int: the clients table key.

    Returns:
        client if existent. None otherwise.
    """
    try:
        redis_key = f"client:{clientNbr}"
        cached_client = c.cache_get(redis_key)
        if cached_client:
            return cached_client
        
        query = {"clientNbr": clientNbr}
        client = CLIENTS.find_one(query)

        if client:#caching
            c.cache_set(redis_key, client)
            
        return client
    except Exception as e:
        print(f"Error finding client: {e}")
        return None

@getClient.register
def _(name: str, lastName: str):
    """
    Searches for the client with the given name and lastName in database.
    Uses redis caching.

    Args:
        str: the client name.
        str: the client lastName.

    Returns:
        client if existent. None otherwise.
    """
    try:
        redis_key = f"clients:{name}:{lastName}"
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            return cached_clients

        query = {"name": name, "lastName": lastName}
        clients_list = list(CLIENTS.find(query))

        if clients_list:#caching
            c.cache_set(redis_key, clients_list)

        return clients_list
    except Exception as e:
        print(f"Error finding client: {e}")
        return None
    
def getClientSpent(clientNbr: int):
    return None#TODO doit

def getAllClients():
    """
    Searches for all the clients in database.
    Caches query afterwards.

    Returns:
        client list if existent. None otherwise.
    """
    try:
        redis_key = f"clients:all"
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            return cached_clients

        clients = CLIENTS.find()

        clients_list = list(clients)

        if clients_list:  #caching#TODO capaz si se podria cachear solo la query getall, pero habria que chequear en toda fncion que modifique toda la db
            redis_key = f"clients:all"#TODO magic query string!
            c.cache_set(redis_key, clients_list)
        
        return clients_list
    except Exception as e:
        print(f"Error finding all clients: {e}")
        return None

def getAllClientsBillAmount():
    return None#TODO doit

def getClientsWithBills():
    return None#TODO doit

def getClientsWithNoBills():
    return None#TODO doit

def getAllPhones():
    """
    Searches for all the phones in database.
    Caches query afterwards.

    Returns:
        phone list if existent. None otherwise.
    """
    try:
        redis_key = f"phones:all"
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            return cached_clients
        
        pipeline = [
            {
                "$match": {
                    "phones": {"$ne": []}
                }
            },
            {
                "$unwind": "$phones"
            },
            {
                "$group": {
                    "_id": {"clientNbr": "$clientNbr", "phone": "$phones.phone"},
                    "clientNbr": {"$first": "$clientNbr"},
                    "name": {"$first": "$name"},
                    "lastName": {"$first": "$lastName"},
                    "address": {"$first": "$address"},
                    "active": {"$first": "$active"}
                }
            }
        ]

        clients_with_phones = CLIENTS.aggregate(pipeline)

        clients_list = list(clients_with_phones)

        if clients_list:  #caching#TODO capaz si se podria cachear solo la query getall, pero habria que chequear en toda fncion que modifique toda la db
            redis_key = f"phones:all"#TODO magic query string!
            c.cache_set(redis_key, clients_list)
        
        return clients_list
    except Exception as e:
        print(f"Error finding all clients: {e}")
        return None
    
#============ Modify ===========>


#============ Delete ===========>
def deleteClient(clientNbr: int):
    try:
        client = getClient(clientNbr)

        if not client:
            print(f"No client with clientNbr {clientNbr}.")
            return True

        CLIENTS.delete_one(query)#TODO habria q borrar las bills relacionadass tmb?
        #TODO ver tema cache que querys corresponde borrar de redis aca, por ahora solo se que esta si
        redis_key = f"clients:all"
        c.cache_delete(redis_key)
        redis_key = f"client:{clientNbr}"
        c.cache_delete(redis_key)
        redis_key = f"clients:{client['name']}:{client['lastName']}"
        c.cache_delete(redis_key)

        return True

    except Exception as e:
        print(f"Error deleting client: {e}")
        return False