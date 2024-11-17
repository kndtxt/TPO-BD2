#============ Imports ==================>
from persistence.persistence import mydb, mongoClient, CLIENTS
import persistence.cache as c
from models import Client
from pydantic import ValidationError
from functools import singledispatch
from pymongo.errors import DuplicateKeyError

#============ Setters ==================>
def insertClient(client: Client):
    """
    Inserts client into database.

    Args:
        client dictionary, according the Client model

    Returns:
        client if created. None otherwise.
    """ 
    try:
        client = client.model_dump()
        newClient = CLIENTS.insert_one(client)        
        #update cache
        if len(client['phones'])>0:
            redis_key = f"phones:all"
            c.cache_del(redis_key)
        redis_key = f"clients:all"
        c.cache_del(redis_key)
        redis_key = f"clients:{client['name']}:{client['lastName']}"
        c.cache_del(redis_key)

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
            cached_client.pop('billNbrs', None)     #drop fields not part of the ERD
            cached_client.pop('_id', None)
            return cached_client

        query = {"clientNbr": clientNbr}
        client = CLIENTS.find_one(query)

        if client:#caching
            c.cache_set(redis_key, client)
            client.pop('billNbrs', None)
            client.pop('_id', None)
            
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
            for client in cached_clients:
                client.pop('billNbrs', None)
                client.pop('_id', None)
            return cached_clients

        query = {"name": name, "lastName": lastName}
        clients_list = list(CLIENTS.find(query))

        if clients_list:#caching
            c.cache_set(redis_key, clients_list)
            for client in clients_list:
                client.pop('billNbrs', None)
                client.pop('_id', None)

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
            for client in cached_clients:
                client.pop('billNbrs', None)
                client.pop('_id', None)
            return cached_clients

        clients = CLIENTS.find()
        clients_list = list(clients)

        if clients_list:  
            redis_key = f"clients:all"
            c.cache_set(redis_key, clients_list)
            for client in clients_list:
                client.pop('billNbrs', None)
                client.pop('_id', None)
        
        return clients_list
    except Exception as e:
        print(f"Error finding all clients: {e}")
        return None



def getAllClientsWithBillNbrs():
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
            for client in cached_clients:
                client.pop('_id', None)
            return cached_clients

        clients = CLIENTS.find()
        clients_list = list(clients)

        if clients_list:  
            redis_key = f"clients:all"
            c.cache_set(redis_key, clients_list)
            for client in clients_list:
                client.pop('_id', None)
        
        return clients_list
    except Exception as e:
        print(f"Error finding all clients: {e}")
        return None

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
                "$project": {
                    "_id": 0,
                    "clientNbr": 1,
                    "name": 1, 
                    "lastName": 1, 
                    "address": 1, 
                    "active": 1, 
                    "phone": { 
                        "areaCode": "$phones.areaCode",
                        "phoneNbr": "$phones.phoneNbr",
                        "phoneType": "$phones.phoneType"
                    }
                }
            }
        ]

        clients_with_phones = CLIENTS.aggregate(pipeline)

        clients_list = list(clients_with_phones)

        #load query to cache
        if clients_list: 
            redis_key = f"phones:all"
            c.cache_set(redis_key, clients_list)

        return clients_list
    except Exception as e:
        print(f"Error finding all phones: {e}")
        return None
    
def getClientsWithBillAmount():
    try:
        all_clients =  getAllClientsWithBillNbrs()
        if all_clients:
            for client in all_clients:
                if 'billNbrs' in client:
                    client['billAmount'] = len(client['billNbrs'])
                else:
                    client['billAmount'] = 0
                client.pop('billNbrs', None)
            return all_clients
        else:
            return None
    except Exception as e:
        print(f"Error finding all clients with bill amount: {e}")
        return None

def getClientsWithBills():
    try:
        all_clients =  getAllClientsWithBillNbrs()
        if all_clients:
            all_clients_with_bills = [client for client in all_clients if 'billNbrs' in client and client['billNbrs']]
            for client in all_clients_with_bills:
                client.pop('billNbrs', None)
            return all_clients_with_bills

        else:
            return None
    except Exception as e:
        print(f"Error finding all clients with bills: {e}")
        return None

def getClientsWithNoBills():
    try:
        all_clients =  getAllClientsWithBillNbrs()
        if all_clients:
            all_clients_without_bills = [client for client in all_clients if len(client['billNbrs'])==0]
            for client in all_clients_without_bills:
                client.pop('billNbrs', None)
            return all_clients_without_bills

        else:
            return None
    except Exception as e:
        print(f"Error finding all clients without bills: {e}")
        return None
    
#============ Modify ===========>

def modifyClient(client: Client):
    """
    Modifies a persisted client.
    Args:
        fiter(object): the filter that matches with clients to modify.
    Returns:
        true if modified. false otherwise
    """
    try:
        client = client.model_dump()
        filter = {"clientNbr": client['clientNbr']}
        fields = {}
        for key, value in client.items():
            if key != "_id" and key != "clientNbr":
                fields[key] = value
        operation = {"$set": fields}
        result = CLIENTS.update_one(filter, operation)
        if result.modified_count <=0: raise Exception("No clients modified")
        if result:    #update cache
            redis_key = f"client:{client['clientNbr']}"
            c.cache_del(redis_key)
            redis_key = f"clients:{client['name']}:{client['lastName']}"
            c.cache_del(redis_key)
            redis_key = f"clients:all"
            c.cache_del(redis_key)
            redis_key = f"phones:all"
            c.cache_del(redis_key)
            #TODO habria q borrar las bills relacionadass tmb?
        return True

    except Exception as e:
        print(f"Error finding all clients: {e}")
        return None

#============ Delete ===========>
def deleteClient(clientNbr: int):
    try:
        client = getClient(clientNbr)

        if not client:
            print(f"No client with clientNbr {clientNbr}.")
            return True
        
        query = {"clientNbr":clientNbr}
        CLIENTS.delete_one(query)#TODO habria q borrar las bills relacionadass tmb?

        #update cache
        if len(client['phones']) > 0:
            redis_key = f"phones:all"
            c.cache_del(redis_key)
        redis_key = f"clients:all"
        c.cache_del(redis_key)
        redis_key = f"client:{clientNbr}"
        c.cache_del(redis_key)
        redis_key = f"clients:{client['name']}:{client['lastName']}"
        c.cache_del(redis_key)
        #TODO habria q borrar las bills relacionadass tmb?

        return True

    except Exception as e:
        print(f"Error deleting client: {e}")
        return False