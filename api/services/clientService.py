#============ Imports ==================>
from persistence.persistence import CLIENTS, BILLS
import persistence.cache as c
from models import Client
from pydantic import ValidationError
from functools import singledispatch
from pymongo.errors import DuplicateKeyError
from utils.json_serialize_utils import clean_data

#============ Setters ==================>
def insertClient(client: Client):
    '''
    Inserts client into database.

    Args:
        client dictionary, according the Client model

    Returns:
        client if created. None otherwise.
    ''' 
    try:
        client = client.model_dump()
        newClient = CLIENTS.insert_one(client)        
        #update cache
        if len(client['phones']) > 0:
            redis_key = 'phones:all'
            c.cache_del(redis_key)
        redis_key = 'clients:all'
        c.cache_del(redis_key)
        name = client['name']
        surname = client['lastName']
        redis_key = f'clients:{name}:{surname}'
        c.cache_del(redis_key)

        return newClient

    except ValidationError as e:
        print(f'Data validation error: {e}')
    except DuplicateKeyError as e:
        print(f'Client for nroCliente: {client["clientNbr"]} already exists!')
        return None
    except Exception as e:
        print(e)
        return None

#============ Getters ===========>
@singledispatch
def getClient(*client):
    raise NotImplementedError(f'Unsupported type: {type(client)}')

@getClient.register
def _(clientNbr: int):
    '''
    Searches for the client with the given clientNbr in database.
    Uses redis caching.

    Args:
        int: the clients table key.

    Returns:
        client if existent. None otherwise.
    '''
    try:
        redis_key = f'client:{clientNbr}'
        cached_client = c.cache_get(redis_key)
        if cached_client:
            return cached_client

        query = {'clientNbr': clientNbr}
        projection = {'_id': 0}
        client = CLIENTS.find_one(query, projection)

        if client:
            client.pop('billNbrs', None)
            c.cache_set(redis_key, client)
        
        return client
    except Exception as e:
        print(f'Error finding client: {e}')
        return None

@getClient.register
def _(name: str, lastName: str):
    '''
    Searches for the client with the given name and lastName in database.
    Uses redis caching.

    Args:
        str: the client name.
        str: the client lastName.

    Returns:
        client if existent. None otherwise.
    '''
    try:
        redis_key = f'clients:{name}:{lastName}'
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            return cached_clients

        query = {'name': name, 'lastName': lastName}
        projection = {'_id': 0, 'billNbrs': 0}
        clients_list = clean_data(CLIENTS.find(query, projection))

        if len(clients_list) > 0:
            c.cache_set(redis_key, clients_list)

        return clients_list
    except Exception as e:
        print(f'Error finding client: {e}')
        return None
    

def getAllClients():
    '''
    Searches for all the clients in database.
    Caches query afterwards.

    Returns:
        client list if existent. None otherwise.
    '''
    try:
        redis_key = 'clients:all'
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            for client in cached_clients:
                client.pop('billNbrs', None)
            return cached_clients


        projection = {'_id': 0}
        clients = clean_data(CLIENTS.find({}, projection))

        if len(clients) > 0:  
            c.cache_set(redis_key, clients)
        
        for client in clients:
            client.pop('billNbrs', None)

        return clients
    except Exception as e:
        print(f'Error finding all clients: {e}')
        return None



def getAllClientsWithBillNbrs():
    '''
    Searches for all the clients in database.
    Caches query afterwards.

    Returns:
        client list if existent. None otherwise.
    '''
    try:
        redis_key = 'clients:all'
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            return cached_clients

        projection = {'_id': 0}
        clients = clean_data(CLIENTS.find({}, projection))

        if clients:  
            c.cache_set(redis_key, clients)
        
        return clients
    except Exception as e:
        print(f'Error finding all clients: {e}')
        return None

def getAllPhones():
    '''
    Searches for all the phones in database.
    Caches query afterwards.

    Returns:
        phone list if existent. None otherwise.
    '''
    try:
        redis_key = 'phones:all'
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            return cached_clients

        pipeline = [
            {
                '$match': {
                    'phones': {'$ne': []}
                }
            },
            {
                '$unwind': '$phones'
            },
            {
                '$project': {
                    '_id': 0,
                    'clientNbr': 1,
                    'name': 1, 
                    'lastName': 1, 
                    'address': 1, 
                    'active': 1, 
                    'phone': { 
                        'areaCode': '$phones.areaCode',
                        'phoneNbr': '$phones.phoneNbr',
                        'phoneType': '$phones.phoneType'
                    }
                }
            }
        ]

        clients_with_phones = clean_data(CLIENTS.aggregate(pipeline))

        #load query to cache
        if len(clients_with_phones) > 0: 
            c.cache_set(redis_key, clients_with_phones)

        return clients_with_phones
    except Exception as e:
        print(f'Error finding all phones: {e}')
        return None
    
def getClientsWithBillAmount():
    try:
        all_clients = getAllClientsWithBillNbrs()
        if all_clients and len(all_clients) > 0:
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
        print(f'Error finding all clients with bill amount: {e}')
        return None

def getClientsWithBills():
    try:
        all_clients = getAllClientsWithBillNbrs()
        if all_clients:
            all_clients_with_bills = [client for client in all_clients if 'billNbrs' in client and len(client['billNbrs']) > 0]
            for client in all_clients_with_bills:
                client.pop('billNbrs', None)
            return all_clients_with_bills
        else:
            return None
    except Exception as e:
        print(f'Error finding all clients with bills: {e}')
        return None

def getClientsWithNoBills():
    try:
        all_clients =  getAllClientsWithBillNbrs()
        if all_clients:
            all_clients_without_bills = [client for client in all_clients if len(client['billNbrs']) == 0]
            for client in all_clients_without_bills:
                client.pop('billNbrs', None)
            return all_clients_without_bills
        else:
            return None
    except Exception as e:
        print(f'Error finding all clients without bills: {e}')
        return None
    
def getClientTotalWithTaxes():
    '''
    Gets all the clients' name and surnames with their total spent

    Returns:
        List of client name and surnames with their total spent. None otherwise
    '''
    try:
        pipeline = [
            {
                '$group': {
                    '_id': '$clientNbr',
                    'total_with_taxes': { '$sum': '$taxxedTotal'}
                }
            },
            {
                '$lookup': {
                    'from': CLIENTS.name,
                    'localField': '_id',
                    'foreignField': 'clientNbr',
                    'as': 'client'
                }
            },
            {
                '$unwind': '$client'
            },
            {
                '$replaceRoot': {
                    'newRoot': {
                        '$mergeObjects': ['$client', {'total_with_taxes': '$total_with_taxes'}]
                    }
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'name': 1,
                    'lastName': 1,
                    'total_with_taxes': 1,
                }
            }
        ]
        bills_by_clientNbr = clean_data(BILLS.aggregate(pipeline))
        
        return bills_by_clientNbr
    
    except Exception as e:
        print(f'Error finding bills bought by that client: {e}')
        return None
    
#============ Modify ===========>

def modifyClient(client: Client):
    '''
    Modifies a persisted client.
    Args:
        Client. Client to modify
    Returns:
        true if modified. false otherwise
    '''
    try:
        client = client.model_dump()
        clientNbr = client['clientNbr']
        filter = {'clientNbr': clientNbr}
        fields = {}
        for key, value in client.items():
            if key != '_id' and key != 'clientNbr':
                fields[key] = value
        operation = {'$set': fields}
        result = CLIENTS.update_one(filter, operation)
        if result.modified_count <= 0: raise Exception('No clients modified')
        if result:    #update cache
            redis_key = f'client:{clientNbr}'
            c.cache_del(redis_key)
            name = client['name']
            surname = client['lastName']
            redis_key = f'clients:{name}:{surname}'
            c.cache_del(redis_key)
            redis_key = 'clients:all'
            c.cache_del(redis_key)
            redis_key = 'phones:all'
            c.cache_del(redis_key)
            #TODO habria q borrar las bills relacionadass tmb?
        return True
    
    except Exception as e:
        print(f'Error finding all clients: {e}')
        return None

#============ Delete ===========>
def deleteClient(clientNbr: int):
    try:
        client = getClient(clientNbr)
        if not client:
            print(f'No client with clientNbr {clientNbr}.')
            return False
        
        query = {'clientNbr': clientNbr}
        CLIENTS.delete_one(query)#TODO habria q borrar las bills relacionadass tmb?
        #update cache
        if len(client['phones']) > 0:
            redis_key = 'phones:all'
            c.cache_del(redis_key)
        redis_key = 'clients:all'
        c.cache_del(redis_key)
        redis_key = f'client:{clientNbr}'
        name = client['name']
        surname = client['lastName']
        c.cache_del(redis_key)
        redis_key = f'clients:{name}:{surname}'
        c.cache_del(redis_key)
        #TODO habria q borrar las bills relacionadass tmb?

        return True

    except Exception as e:
        print(f'Error deleting client: {e}')
        return False