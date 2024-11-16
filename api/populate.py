import persistence.persistence as p
import persistence.cache as c
import services.billService as bs
import services.productService as ps

def main():
    c.flushCache()
    p.drop_all_tables()
    p.populateDb()  # This function will populate the database with the data from the csv files  

    #view test
    view = bs.createBillDataView()
    for bill in view:
        print(f"bill data: {bill} \n")

    unbilled = ps.createProductsNotBilledView()
    for product in unbilled:
        print(f"Unbilled product: {product}\n")


   
if __name__ == '__main__':
    main()