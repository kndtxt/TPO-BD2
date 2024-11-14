#============ Imports ==================>

import redis
import pymongo
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

#============ Clients ===========>
clients = mongoClient["DB2TPE"]["clients"]
def insertClient(nroCliente, nombre, apellido, direccion, activo, codigoArea, nroTel, tipoTel):
    try:
        newClient = clients.insert_one({"nroCliente": nroCliente,
                            "nombre": nombre,
                            "apellido": apellido,
                            "direccion": direccion,
                            "activo": activo,
                            "telefono": {"codigoArea": codigoArea,
                                        "nroTel": nroTel,
                                        "tipoTel": tipoTel}})
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
def _(client: int):
    try:
        query = {"nroCliente": client}
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
    insertClient(1, "John", "Doe", "Calle Falsa 123", True, 11, 12345678, "Celular")
    insertClient(2, "Jane", "Doe", "Calle Falsa 123", True, 11, 12345678, "Celular")
    print(getClient("Jane", "Doe"))
    print(getClient(1))

main()


