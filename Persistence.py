#============ Imports ==================>

import pymongo
import cache as c
from pydantic import ValidationError
from models import Cliente, Telefono
from functools import singledispatch        #provides method overloading among other things
import csv

#============ Dbs Connection ===========>

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = mongoClient["mydatabase"]    #Mongo only creates a db when it gets content

#============ Clients ===========>
clients = mongoClient["DB2TPE"]["clients"]
clients.create_index([('nroCliente', 1)], unique=True)

def insertClient(client):
    try:
        redis_key = f"clientes:{client['nombre']}:{client['apellido']}"#forzamos borrado en redis si estaba cacheado
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            c.cache_del(redis_key)

        
        nroCliente = int(client['nroCliente']) if isinstance(client['nroCliente'], str) else client['nroCliente']
        query = {"nroCliente": nroCliente}
        aux_client = clients.find_one(query)
        if aux_client is not None:
            print(f"Client for nroCliente: {nroCliente} already exists!")
            return None

        aux_client = Cliente(**client)#validamos segun model
        newClient = clients.insert_one(aux_client.dict())
        return newClient

    except ValidationError as e:
        print(f"Data validation error: {e}")
    except Exception as e:
        print(e)
        return None

@singledispatch
def getClient(*client):
    raise NotImplementedError(f"Unsupported type: {type(client)}")

@getClient.register
def _(nroCliente: int):
    try:
        redis_key = f"cliente:{nroCliente}"
        cached_client = c.cache_get(redis_key)
        if cached_client:
            return cached_client

        query = {"nroCliente": nroCliente}
        client = clients.find_one(query)

        if client:#cacheamos
            c.cache_set(redis_key, client)
            
        return client
    except Exception as e:
        print(f"Error finding client: {e}")
        return None

@getClient.register
def _(nombre: str, apellido: str):
    try:

        redis_key = f"clientes:{nombre}:{apellido}"
        cached_clients = c.cache_get(redis_key)
        if cached_clients:
            return cached_clients

        query = {"nombre": nombre, "apellido": apellido}
        clients_list = list(clients.find(query))

        if clients_list:#cacheamos
            c.cache_set(redis_key, clients_list)

        return clients_list
    except Exception as e:
        print(f"Error finding client: {e}")
        return None


def populateDb():
    clientes = {}

    with open('./resources/e01_cliente.csv', mode="r", encoding='ISO-8859-1') as clientsFile:
        clientsReader = csv.reader(clientsFile, delimiter=';')
        ClientHeaders = next(clientsReader)   #skip headers

        for row in clientsReader:
            nroCliente = row[0]
            nombre = row[1]
            apellido = row[2]
            direccion = row[3]
            activo = row[4]
            clientes[nroCliente] = {
                "nroCliente": nroCliente,
                "nombre": nombre,
                "apellido": apellido,
                "direccion": direccion,
                "activo": activo,
                "telefonos": [] 
            }
        
    with open('./resources/e01_telefono.csv', mode="r",encoding='ISO-8859-1') as phonesFile:
        phonesReader = csv.reader(phonesFile, delimiter=';')
        phoneHeaders = next(phonesReader)

        for row in phonesReader:

            nroCliente = row[3]
            if "telefonos" not in clientes[nroCliente]:     #if the key does not exist, create it
                clientes[nroCliente]["telefonos"] = []

            clientes[nroCliente]["telefonos"].append({
                "codigoArea": row[0],   
                "nroTel": row[1],
                "tipoTel": row[2]
            })

    for cliente in clientes:
        insertClient(clientes[cliente])
            



