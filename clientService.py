#============ Imports ==================>
from persistence import mydb, mongoClient
from productService import getProduct
import cache as c
from models import Cliente
from pydantic import ValidationError
from functools import singledispatch

#============ Dbs Connection ===========>
CLIENTS = mydb["clients"]
CLIENTS.create_index([('nroCliente', 1)], unique=True)

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
        
        nroCliente = int(client['nroCliente']) if isinstance(client['nroCliente'], str) else client['nroCliente']
        query = {"nroCliente": nroCliente}
        aux_client = CLIENTS.find_one(query)
        if aux_client is not None:
            print(f"Client for nroCliente: {nroCliente} already exists!")
            return None

        aux_client = Cliente(**client)#validate by model
        newClient = CLIENTS.insert_one(aux_client.dict())
        return newClient

    except ValidationError as e:
        print(f"Data validation error: {e}")
    except Exception as e:
        print(e)
        return None

#============ Getters ===========>
@singledispatch
def getClient(*client):
    raise NotImplementedError(f"Unsupported type: {type(client)}")

@getClient.register
def _(nroCliente: int):
    """
    Searches for the client with the given nroCliente in database.
    Uses redis caching.

    Args:
        int: the clients table key.

    Returns:
        client if existent. None otherwise.
    """
    try:
        redis_key = f"client:{nroCliente}"
        cached_client = c.cache_get(redis_key)
        if cached_client:
            return cached_client

        query = {"nroCliente": nroCliente}
        client = CLIENTS.find_one(query)

        if client:#caching
            c.cache_set(redis_key, client)
            
        return client
    except Exception as e:
        print(f"Error finding client: {e}")
        return None

@getClient.register
def _(nombre: str, apellido: str):
    """
    Searches for the client with the given nombre and apellido in database.
    Uses redis caching.

    Args:
        str: the client name.
        str: the client surname.

    Returns:
        client if existent. None otherwise.
    """
    try:
        redis_key = f"clients:{nombre}:{apellido}"
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            return cached_clients

        query = {"nombre": nombre, "apellido": apellido}
        clients_list = list(CLIENTS.find(query))

        if clients_list:#caching
            c.cache_set(redis_key, clients_list)

        return clients_list
    except Exception as e:
        print(f"Error finding client: {e}")
        return None
    
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

'''def getAllPhones():
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
        
        clients = CLIENTS.find({telefonos: {"$ne": []}})
        CLIENTS.aggregate({$match:})

        clients_with_phones = []

        clients_list = list(clients)

        if clients_list:  #caching#TODO capaz si se podria cachear solo la query getall, pero habria que chequear en toda fncion que modifique toda la db
            redis_key = f"clients:all"#TODO magic query string!
            c.cache_set(redis_key, clients_list)
        
        return clients_list
    except Exception as e:
        print(f"Error finding all clients: {e}")
        return None'''
    
#============ Modify ===========>


#============ Delete ===========>
def deleteClient(nroCliente: int):
    try:
        client = getClient(nroCliente)

        if not client:
            print(f"No client with nroCliente {nroCliente}.")
            return True

        CLIENTS.delete_one(query)#TODO habria q borrar las bills relacionadass tmb?
        #TODO ver tema cache que querys corresponde borrar de redis aca, por ahora solo se que esta si
        redis_key = f"cliente:{nroCliente}"
        c.cache_delete(redis_key)

        return True

    except Exception as e:
        print(f"Error al eliminar cliente: {e}")
        return False