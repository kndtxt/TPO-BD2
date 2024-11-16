import api.persistence.persistence as p
import api.persistence.cache as c

def main():
    c.flushCache()
    p.drop_all_tables()
    p.populateDb()  # This function will populate the database with the data from the csv files   

    p.session.end_session()   #end session and abort all ongoing transactions

if __name__ == '__main__':
    main()