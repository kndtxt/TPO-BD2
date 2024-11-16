#============ Imports ==================>
from api.persistence.persistence import session, BILLS, CLIENTS, PRODUCTS
from .productService import getProduct
import api.persistence.cache as c
from models import Bill
from pydantic import ValidationError

#session to allow transactional behaviour

#============ Setters ==================>

def insertBill(bill): 
    """
    Populates db with provided dataset. Assumes stocks need not be updated.
    Args:
        bill(Bill): the bill to be inserted
    """ 
    try:
        oldClientNbr = bill['clientNbr']
        clientNbr = int(oldClientNbr) if isinstance(oldClientNbr, str) else oldClientNbr
        clientQuery = {"clientNbr": clientNbr}
        operation = {"$push": {"billNbrs": bill["billNbr"]}} 
        updateClient = CLIENTS.update_one(clientQuery, operation)       #add reference to bill that client has purchased
        if updateClient.matched_count <= 0: raise Exception(f"Client for bill not found.")
        
        for detail in bill["details"]:
            oldCodProduct = detail['codProduct']
            codProduct = int(oldCodProduct) if isinstance(oldCodProduct, str) else oldCodProduct
            productQuery = {"codProduct": codProduct}
            updateProduct = PRODUCTS.update_one(productQuery, operation)    #add reference to bill where product was billed
            if updateProduct.matched_count <= 0: raise Exception(f"Product for bill not found.")             

        aux_bill = Bill(**bill)#validate by model
        newBill = BILLS.insert_one(aux_bill.model_dump())
        return newBill
    except ValidationError as e:
        print(f"Data validation error: {e}")
    except Exception as e:
        print(f'Cannot insert bill: {e}')


def insertNewBill(bill):
    """
    Insert given bill into db and updates product stock with transactional behaviour.
    Args:
        bill(Bill): the bill to be inserted
    Returns:
        Bill if inserted. None otherwise.
    """ 
    try:
        session.start_transaction()
        insertBill(bill)
        for detail in bill["details"]:
            productNbr = detail["productNbr"]
            product = getProduct(productNbr)
            
            if product is None:
                session.abort_transaction()
                raise Exception(f"Product to bill not found")
            
            newStock = product.stock - (detail.amount)
            if newStock<0: 
                session.abort_transaction()
                raise Exception(f"Requested more items than available stock")
            
            productQuery = {"prodctNbr": productNbr}
            operation = {"$set":{"stock":newStock}}
            result = PRODUCTS.update_one(productQuery, operation)
            if result.matched_count <= 0:
                session.abort_transaction()
                raise Exception(f"Billing error")
            
        session.commit_transaction()
    except Exception as e:
        print("Billing error: {e}")
        return None

#============ Getters ==================>
