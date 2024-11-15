import persistence as p
import clientService as cs

def main():
    p.populateDb()  # This function will populate the database with the data from the csv files
    print(cs.getClient("Jacob", "Cooper"))
    print(cs.getClient(20))

    p.session.end_session()   #end session and abort all ongoing transactions

main()