import persistence.persistence as p
import persistence.cache as c
import services.billService as bs
import services.productService as ps
import services.clientService as cs
from models import Client, Product

def main():
    c.flushCache()
    p.drop_all_tables()
    p.populateDb()  # This function will populate the database with the data from the csv files  

    #query 1
    print("req 1 (son 100)")
    print(len(cs.getAllClients()))
    
    #query 2
    print("req 2")
    print(cs.getClient("Jacob", "Cooper"))
    
    #query 3
    print("req 3 (son 198)")
    print(len(cs.getAllPhones()))

    #query 4
    print("req 4")
    print(cs.getClientsWithBills())

    #query 5
    print("req 5")
    print(cs.getClientsWithNoBills())

    #query 6
    print("req 6")
    print(cs.getClientsWithBillAmount())

    #print("req 7") TODO

    #query 8
    print("req 8")
    print(ps.getAllBoughtProducts())


#print("req 9") TODO
    #print()
    #print("req 10") TODO
    #print()

    #query 11   
    print("req 11") 
    print()
    view = bs.createBillDataView()
    for bill in view:
        print(f"bill data: {bill} \n")

    #query 12
    print("req 12")
    print()
    unbilled = ps.createProductsNotBilledView()
    for product in unbilled:
        print(f"Unbilled product: {product}\n")

    print("req 13| create")
    cs.insertClient(Client(
                clientNbr = 105,
                name= "notCambio",
                lastName= "notcambio",
                address= "notcambio",
                active= 76,
                phones= [], 
                billNbrs= [2]))
    print(cs.getClient(105))
    print("req 13| modify")
    cs.modifyClient(Client(
                clientNbr = 105,
                name= "cambio",
                lastName= "cambio",
                address= "cambio",
                active= 76,
                phones= [], 
                billNbrs= [2]
            ))
    print(cs.getClient(105))
    print("req 13| delete")
    cs.deleteClient(105)
    print(cs.getClient(105))
    print("req 14| create")
    ps.insertProduct(Product(
                codProduct= 105,
                brand= "starlight",
                name= "saracatunga",
                description= "heyo",
                price= 6.8,
                stock= 8,
                billNbrs= [2]
            ))
    print(ps.getProduct(105))
    print("req 14| modify")
    ps.modifyProduct(Product(
                codProduct= 105,
                brand= "saracatunga",
                name= "saracatungan't",
                description= "heyon't",
                price= 6.8,
                stock= 8,
                billNbrs= [2]
    ))
    print(ps.getProduct(105))



   
if __name__ == '__main__':
    main()