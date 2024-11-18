import persistence.persistence as p
import persistence.cache as c

def main():
    c.flushCache()
    p.drop_all_tables()
    p.populateDb()  # This function will populate the database with the data from the csv files  

if __name__ == '__main__':
    main()