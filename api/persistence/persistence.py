#============ Imports ==================>
import pymongo
import csv
from datetime import datetime, date
#============ Dbs Connection ===========>
mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = mongoClient["DB2TPE"]    #Mongo only creates a db when it gets content

def drop_all_tables():
    if "bills" in mydb.list_collection_names():
        mydb["bills"].drop()
    if "clients" in mydb.list_collection_names():
        mydb["clients"].drop()
    if "products" in mydb.list_collection_names():
        mydb["products"].drop()
    if "notBilledProducts" in mydb.list_collection_names():
        mydb["notBilledProducts"].drop()
    if "billDataByDate" in mydb.list_collection_names():
        mydb["billDataByDate"].drop()

BILLS = mydb["bills"]
BILLS.create_index([('billNbr', 1)], unique=True)
CLIENTS = mydb["clients"]
CLIENTS.create_index([('clientNbr', 1)], unique=True)
PRODUCTS = mydb["products"]
PRODUCTS.create_index([('codProduct', 1)], unique=True)
session = mongoClient.start_session()

#=== POPULATOR ===>
def populateDb():

#==== CLient Data ====>
    clients = {}

    with open('./resources/e01_cliente.csv', mode="r", encoding='ISO-8859-1') as clientsFile:
        clientsReader = csv.reader(clientsFile, delimiter=';')
        ClientHeaders = next(clientsReader)   #skip headers

        for row in clientsReader:
            clientNbr = row[0]
            name = row[1]
            lastName = row[2]
            address = row[3]
            active = row[4]
            clients[clientNbr] = {
                "clientNbr": int(clientNbr),
                "name": name,
                "lastName": lastName,
                "address": address,
                "active": int(active),
                "phones": [], 
                "billNbrs": []
            }
        
    with open('./resources/e01_telefono.csv', mode="r",encoding='ISO-8859-1') as phonesFile:
        phonesReader = csv.reader(phonesFile, delimiter=';')
        phoneHeaders = next(phonesReader)

        for row in phonesReader:
            clientNbr = row[3]
            if "phones" not in clients[clientNbr]:     #if the key does not exist, create it
                clients[clientNbr]["phones"] = []

            clients[clientNbr]["phones"].append({
                "areaCode": int(row[0]),   
                "phoneNbr": int(row[1]),
                "phoneType": row[2]
            })
    for client in clients:
            CLIENTS.insert_one(clients[client])


#==== Product Data ====>

    products = {}
    with open('./resources/e01_producto.csv', mode="r",encoding='ISO-8859-1') as productFile:
        productReader = csv.reader(productFile, delimiter=';')
        productHeader = next(productReader)

        for row in productReader:
            codProduct = row[0]
            products[codProduct] = {
                "codProduct": int(codProduct),
                "brand": row[1],
                "name" : row[2],
                "description" : row[3],
                "price" : float(row[4]),
                "stock" : int(row[5]),
                "billNbrs" : []      #when a bill is inserted, id is added to the list
            }
    for product in products:
        PRODUCTS.insert_one(products[product])
        
#==== Factura Data ====>
    bills = {}
    with open('./resources/e01_factura.csv', mode="r",encoding='ISO-8859-1') as billFile:
        billReader = csv.reader(billFile, delimiter=';')
        billHeader = next(billReader)

        for row in billReader:
            billNbr = row[0]
            clientNbr = row[5]
            bills[billNbr] = {
                "billNbr": int(billNbr),
                "date": datetime.strptime(row[1], "%Y-%m-%d"),
                "total": float(row[2]),
                "tax": float(row[3]),
                "taxxedTotal": float(row[4]),
                "clientNbr": int(clientNbr),
                "details": []
            }

        with open('./resources/e01_detalle_factura.csv', mode="r",encoding='ISO-8859-1') as billDetailFile:
            billDetailReader = csv.reader(billDetailFile, delimiter=';')
            billDetailHeader = next(billDetailReader)

            for row in billDetailReader:
                billNbr = row[0]
                bills[billNbr]["details"].append({
                    "codProduct": int(codProduct),
                    "itemNbr": int(row[2]),
                    "amount": float(row[3]),
                })
    
    for billIndex in bills:
        bill = bills[billIndex]
        clientQuery = {"clientNbr": int(bill["clientNbr"])}
        operation = {"$push": {"billNbrs": bill["billNbr"]}} 
        updateClient = CLIENTS.update_one(clientQuery, operation)       #add reference to bill that client has purchased        
        for detail in bill["details"]:
            productQuery = {"codProduct": int(detail['codProduct'])}
            updateProduct = PRODUCTS.update_one(productQuery, operation)    #add reference to bill where product was billed
        BILLS.insert_one(bills[billIndex])

            



