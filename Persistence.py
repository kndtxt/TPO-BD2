#============ Imports ==================>

import redis
import pymongo
from functools import singledispatch        #provides method overloading among other things
import csv

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

#============ Clients ===========>
clients = mongoClient["DB2TPE"]["clients"]

def insertClient(nroCliente, nombre, apellido, direccion, activo, codigoArea=None, nroTel=None, tipoTel=None):
    try:
        client = {"nroCliente": nroCliente,
                "nombre": nombre,
                "apellido": apellido,
                "direccion": direccion,
                "activo": activo}
        if codigoArea and nroTel and tipoTel:
            client["telefono"] = {"codigoArea": codigoArea,
                                "nroTel": nroTel,
                                "tipoTel": tipoTel}
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


#============ Main ===========>
def main():

    clientes = {}
    with open('./resources/e01_cliente.csv', mode="r", encoding='ISO-8859-1') as clientsFile:
        clientsReader = csv.reader(clientsFile, delimiter=';')
        ClientHeaders = next(clientsReader)   #skip headers
        for row in clientsReader:
            print(row)
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
        for row in phonesReader:
            codigoArea = row[0]
            nroTel = row[1]
            tipoTel = row[2]
            nroCliente = row[3]
            clientes[nroCliente]["telefono"] = {
                "codigoArea": codigoArea,
                "nroTel": nroTel,
                "tipoTel": tipoTel
            }
    for cliente in clientes:
        print(clientes[cliente])
        tempTelefono = clientes[cliente].get("telefono")
        if tempTelefono:
            insertClient(cliente, 
                clientes[cliente]["nombre"], 
                clientes[cliente]["apellido"],
                clientes[cliente]["direccion"],
                clientes[cliente]["activo"],
                tempTelefono["codigoArea"],
                tempTelefono["nroTel"],
                tempTelefono["tipoTel"])
        else:
            insertClient(cliente, 
                clientes[cliente]["nombre"], 
                clientes[cliente]["apellido"],
                clientes[cliente]["direccion"],
                clientes[cliente]["activo"])

    for i in range(1, 100):
        tempClient = getClient(i)
        print(tempClient.get("nombre"))
        if tempClient.get("telefono"):
            print(tempClient.get("telefono").get("nroTel"))
            
main()


