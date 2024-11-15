import Persistence as p

def main():
    p.populateDb()  # This function will populate the database with the data from the csv files
    print(p.getClient("Jacob", "Cooper"))

main()