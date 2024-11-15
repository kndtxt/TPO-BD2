import persistence as p

def main():
    p.populateDb()  # This function will populate the database with the data from the csv files
    print(p.getClient("Jacob", "Cooper"))
    print(p.getClient(1))

    p.session.end_session()   #end session and abort all ongoing transactions

main()