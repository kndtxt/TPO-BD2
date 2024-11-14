#============ Imports ==================>

import redis
import pymongo
from functools import singledispatch        #provides method overloading among other things
import csv

#============ Dbs Connection ===========>

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = mongoClient["mydatabase"]    #Mongo only creates a db when it gets content
r = redis.Redis()

#============ Clients ===========>
clients = mongoClient["DB2TPE"]["clients"]

def insertClient(client):
    try:
        newClient = clients.insert_one(client)
        return newClient
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
        query = {"nroCliente": nroCliente}
        #aca chequeamos si el dato esta cacheado
        #return cached

        client = clients.find_one(query)
        #Aca cacheamos el dato
        return client
    except Exception as e:
        print(f"Error finding client: {e}")
        return None

@getClient.register
def _(nombre: str, apellido: str):
    try:
        query = {"nombre": nombre, "apellido": apellido}
        #Aca me fijo si esta cacheado o no en Redis
        #return cached data
        client = clients.find_one(query)
        return client
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
                "activo": activo
            }
        
    with open('./resources/e01_telefono.csv', mode="r",encoding='ISO-8859-1') as phonesFile:
        phonesReader = csv.reader(phonesFile, delimiter=';')
        phoneHeaders = next(phonesReader)

        if clientes[nroCliente] is None:        #if a client doesn't have personal data asociated, we insert only phone data
            clientes[nroCliente] = {}
            

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
            



