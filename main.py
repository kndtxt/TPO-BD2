import persistence as p
import clientService as cs
import productService as ps
import cache as c

def main():
    c.flushCache()
    p.populateDb()  # This function will populate the database with the data from the csv files  

    print("req 1 (son 100)")
    print(len(cs.getAllClients()))
    print("req 2")
    print(cs.getClient("Jacob", "Cooper"))
    print("req 3 (son 198)")
    print(len(cs.getAllPhones()))
    print("req 4")
    print(cs.getClientsWithBills())
    print("req 5")
    print(cs.getClientsWithNoBills())
    print("req 6")
    print(cs.getClientsWithBillAmount())
    #print("req 7") TODO
    print("req 8")
    print(ps.getAllBoughtProducts())
    #print("req 9") TODO
    #print()
    #print("req 10") TODO
    #print()

    #print("req 11") TODO
    #print()
    #print("req 12") TODO
    #print()

    print("req 13| create")
    cs.insertClient({
                "clientNbr": 105,
                "name": "montoto",
                "lastName": "toteador",
                "address": "heyoo",
                "active": 76,
                "phones": [{
                    "areaCode": 111,   
                    "phoneNbr": 1111111,
                    "phoneType": "F"
                }], 
                "billNbrs": []
            })
    print(cs.getClient(105))
    print("req 13| modify")
    cs.modifyClient({
                "clientNbr": 105,
                "name": "cambio",
                "lastName": "cambio",
                "address": "cambio",
                "active": 76,
                "phones": [], 
                "billNbrs": [2]
            })
    print(cs.getClient(105))
    print("req 13| delete")
    cs.deleteClient(105)
    print(cs.getClient(105))
    print("req 14| create")
    ps.insertProduct({
                "codProduct": 105,
                "brand": "starlight",
                "name" : "saracatunga",
                "description" : "heyo",
                "price" : 6.8,
                "stock" : 8,
                "billNbrs" : [2]
            })
    print(ps.getProduct(105))
    print("req 14| modify")
    ps.modifyProduct({
                "codProduct": 105,
                "brand": "starlight",
                "name" : "saracatunga",
                "description" : "heyo",
                "price" : 10006.8,
                "stock" : 0,
                "billNbrs" : [2]
            })
    print(ps.getProduct(105))
    

    

main()