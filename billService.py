#============ Imports ==================>
from persistence import mydb
import cache as c
from models import Factura
from pydantic import ValidationError
from functools import singledispatch

#============ Dbs Connection ===========>
BILLS = mydb["bills"]
CLIENTS = mydb["clients"]
PRODUCTS = mydb["products"]
BILLS.create_index([('nroFactura', 1)], unique=True)





#============ Setters ==================>

def populateBill(bill): 
    """
    Populates db with provided dataset. Assumes stocks need not be updated.
    Args:
        bill(Bill): the bill to be inserted
    """ 
    try:
        clientQuery = {"clientNbr": bill["clientNbr"]}
        operation = {"$push": {"billNbrs": bill["billNbr"]}} 
        updateClient = CLIENTS.update_one(clientQuery, operation)       #add reference to bill that client has purchased
        if updateClient.matched_count <= 0: raise Exception(f"Client for bill not found.")
        
        for detail in bill["details"]:
            productQuery = {"codProduct": detail["codProduct"]}
            updateProduct = PRODUCTS.update_one(productQuery, operation)    #add reference to bill where product was billed
            if updateProduct.matched_count <= 0: raise Exception(f"Product for bill not found.")             

        newBill = BILLS.insert_one(bill)
        return newBill
    
    except Exception as e:
        print(f'Exception found: {e}')


def insertBill():
    """
    insert.
    Args:
        bill(Bill): the bill to be inserted
    """ 
