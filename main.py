import persistence as p
import clientService as cs
import productService as ps
import cache as c

def main():
    c.flushCache()
    p.populateDb()  # This function will populate the database with the data from the csv files   

    print(ps.insertProduct({
                "codProduct": 105,
                "brand": "strix",
                "name" : "satr",
                "description" : "heyoo",
                "price" : 2.2,
                "stock" : 2,
                "billNbrs" : [1]
    }))
    print("post")
    print(ps.getProduct(105))
    print("all")
    print(ps.getAllProducts())
    print("allbought")
    print(ps.getAllBoughtProducts())
    print(ps.modifyProduct({
                "codProduct": 105,
                "brand": "strix",
                "name" : "MODIFIED",
                "description" : "heyoo",
                "price" : 2.2,
                "stock" : 2,
                "billNbrs" : []
    }))
    print("MODIFIEDallbought")
    print(ps.getAllBoughtProducts())

    #p.session.end_session()   #end session and abort all ongoing transactions

    

main()