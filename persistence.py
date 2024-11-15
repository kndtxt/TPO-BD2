#============ Imports ==================>
import pymongo
import csv
from clientService import insertClient, insertBill
from productService import insertProduct

#============ Dbs Connection ===========>
mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = mongoClient["DB2TPE"]    #Mongo only creates a db when it gets content
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
                "clientNbr": clientNbr,
                "name": name,
                "lastName": lastName,
                "address": address,
                "active": active,
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
                "areaCode": row[0],   
                "phoneNbr": row[1],
                "phoneType": row[2]
            })

        for client in clients:
            insertClient(clients[client])


#==== Product Data ====>

    products = {}
    with open('./resources/e01_producto.csv', mode="r",encoding='ISO-8859-1') as productFile:
        productReader = csv.reader(productFile, delimiter=';')
        productHeader = next(productReader)

        for row in productReader:
            codProduct = row[0]
            products[codProduct] = {
                "codProduct": codProduct,
                "brand": row[1],
                "name" : row[2],
                "description" : row[3],
                "price" : row[4],
                "stock" : row[5],
                "billNbrs" : []      #when a bill is inserted, id is added to the list
            }
        for product in products:
            insertProduct(products[product])
        
#==== Factura Data ====>
    bills = {}
    with open('./resources/e01_factura.csv', mode="r",encoding='ISO-8859-1') as billFile:
        billReader = csv.reader(billFile, delimiter=';')
        billHeader = next(billReader)

        for row in billReader:
            billNbr = row[0]
            clientNbr = row[5]
            bills[billNbr] = {
                "billNbr": billNbr,
                "date": row[1],
                "total": row[2],
                "tax": row[3],
                "taxxedTotal": row[4],
                "clientNbr": clientNbr,
                "details": []
            }

        with open('./resources/e01_detalle_factura.csv', mode="r",encoding='ISO-8859-1') as billDetailFile:
            billDetailReader = csv.reader(billDetailFile, delimiter=';')
            billDetailHeader = next(billDetailReader)

            for row in billDetailReader:
                billNbr = row[0]
                bills[billNbr]["details"].append({
                    "codProduct": codProduct,
                    "itemNbr": row[2],
                    "amount": row[3],
                })
    
    for bill in bills:
        insertBill(bills[bill])

            



