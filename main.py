import persistence as p
import clientService as cs
import productService as ps
import cache as c

def main():
    c.flushCache()
    p.populateDb()  # This function will populate the database with the data from the csv files  

    print("getClient44")
    print(cs.getClient(44))
    print("getAllPhones")
    print(len(cs.getAllPhones()))
    print("getAllClients")
    print(len(cs.getAllClients()))

    #p.session.end_session()   #end session and abort all ongoing transactions

    

main()