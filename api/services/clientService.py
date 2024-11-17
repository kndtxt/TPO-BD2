#============ Imports ==================>
from persistence.persistence import CLIENTS, BILLS
import persistence.cache as c
from models import Client
from functools import singledispatch
from pymongo.errors import DuplicateKeyError
from utils.json_serialize_utils import clean_data
from utils.api_response import ResponseStatus
from fastapi import status

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
        name = client['name']
        surname = client['lastName']
        redis_keys = [
            'clients:all',
            f'clients:{name}:{surname}'
        ]
        c.cache_mdel(redis_keys)

        return newClient

    except DuplicateKeyError as e:
        clientNbr = client['clientNbr']
        return ResponseStatus(status.HTTP_422_UNPROCESSABLE_ENTITY, f'Client for nroCliente: {clientNbr} already exists!')
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')

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
            cached_client.pop('billNbrs', None)
            return cached_client

        query = {'clientNbr': clientNbr}
        projection = {'_id': 0}
        client = CLIENTS.find_one(query, projection)

        if client:
            c.cache_set(redis_key, client)
            client.pop('billNbrs', None)
        else:
            return ResponseStatus(status.HTTP_404_NOT_FOUND, f'Client {clientNbr} not found.')
        return client
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')


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
        projection = {'_id': 0, 'billNbrs': 0} # aca creo que está bien sacar billNbrs dentro de la cache
        clients_list = clean_data(CLIENTS.find(query, projection))

        if len(clients_list) > 0:
            c.cache_set(redis_key, clients_list)

        return clients_list
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')
    

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
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')



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
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')


def getAllPhones(): # TODO: maybe reorder so the first field is phone?
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
                    'phone': { 
                        'areaCode': '$phones.areaCode',
                        'phoneNbr': '$phones.phoneNbr',
                        'phoneType': '$phones.phoneType'
                    },
                    'clientNbr': 1,
                    'name': 1, 
                    'lastName': 1, 
                    'address': 1, 
                    'active': 1, 
                }
            }
        ]

        clients_with_phones = clean_data(CLIENTS.aggregate(pipeline))

        #load query to cache
        if len(clients_with_phones) > 0: 
            c.cache_set(redis_key, clients_with_phones)

        return clients_with_phones
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')

    
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
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')


def getClientsWithBills(): #TODO: maybe simplify into one mongo + redis cache instead of using all
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
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')


def getClientsWithNoBills(): #TODO: maybe simplify into one mongo + redis cache instead of using all
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
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')

    
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
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')

    
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
        if result.modified_count <= 0:
            return ResponseStatus(status.HTTP_404_NOT_FOUND, f'No client with clientNbr {clientNbr}.')
        
        name = client['name']
        surname = client['lastName']
        redis_keys = [
            f'client:{clientNbr}',
            f'clients:{name}:{surname}',
            'clients:all',
            'phones:all',
            'bills:all',
            f'bills:{name}:{surname}'
        ]
        c.cache_mdel(redis_keys)
        #TODO habria q borrar las bills relacionadass tmb? (creo que ya está?)
        return True
    
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')


#============ Delete ===========>
def deleteClient(clientNbr: int):
    try:
        client = getClient(clientNbr)
        if not client:
            return ResponseStatus(status.HTTP_404_NOT_FOUND, f'No client with clientNbr {clientNbr}.')

        
        query = {'clientNbr': clientNbr}
        result = CLIENTS.delete_one(query)#TODO habria q borrar las bills relacionadass tmb? (creo que ya está?)
        if result == 0: # no debería llegar acá pero chequeo extra
            return ResponseStatus(status.HTTP_404_NOT_FOUND, f'No client with clientNbr {clientNbr}.')
        BILLS.delete_many(query)
        #update cache
        if len(client['phones']) > 0:
            redis_key = 'phones:all'
            c.cache_del(redis_key)
        name = client['name']
        surname = client['lastName']
        if len(client['billNbrs']) > 0:
            redis_keys = [
                'bills:all',
                f'bills:{name}:{surname}'
            ]
            c.cache_mdel(redis_keys)
        
        redis_keys = [
            'clients:all',
            f'client:{clientNbr}',
            f'clients:{name}:{surname}',
        ]
        c.cache_mdel(redis_keys)

        return True

    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')
