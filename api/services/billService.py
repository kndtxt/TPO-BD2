#============ Imports ==================>
from persistence.persistence import mydb, mongoClient, session, BILLS, CLIENTS, PRODUCTS
from .productService import getProduct
import persistence.cache as c
from models import Bill
from pydantic import ValidationError
from functools import singledispatch
from datetime import datetime

#session to allow transactional behaviour


#============ Setters ==================>
def insertBill(bill: Bill): 
    """
    Populates db with provided dataset. Assumes stocks need not be updated.
    Args:
        bill(Bill): the bill to be inserted
    """
    try:
        bill_data = bill.model_dump()
        oldClientNbr = bill_data['clientNbr']
        clientNbr = int(oldClientNbr) if isinstance(oldClientNbr, str) else oldClientNbr
        clientQuery = {"clientNbr": clientNbr}
        operation = {"$push": {"billNbrs": bill_data["billNbr"]}}
        updateClient = CLIENTS.update_one(clientQuery, operation)  # add reference to bill that client has purchased
        if updateClient.matched_count <= 0:
            raise Exception(f"Client for bill not found.")
        
        for detail in bill_data["details"]:
            oldCodProduct = detail['codProduct']
            codProduct = int(oldCodProduct) if isinstance(oldCodProduct, str) else oldCodProduct
            productQuery = {"codProduct": codProduct}
            updateProduct = PRODUCTS.update_one(productQuery, operation)  # add reference to bill where product was billed
            if updateProduct.matched_count <= 0:
                raise Exception(f"Product for bill not found.")

        newBill = BILLS.insert_one(bill_data)
        return newBill
    except ValidationError as e:
        print(f"Data validation error: {e}")
    except Exception as e:
        print(f'Cannot insert bill: {e}')

def insertNewBill(bill: Bill):
    """
    Insert given bill into db and updates product stock with transactional behaviour.
    Args:
        bill(Bill): the bill to be inserted
    Returns:
        Bill if inserted. None otherwise.
    """
    try:
        with mongoClient.start_session() as session:
            with session.start_transaction():
                insertBill(bill)
                bill_data = bill.model_dump()
                for detail in bill_data["details"]:
                    productNbr = detail["codProduct"]
                    product = getProduct(productNbr)
                    
                    if product is None:
                        session.abort_transaction()
                        raise Exception(f"Product to bill not found")
                    
                    newStock = product['stock'] - detail['amount']
                    if newStock < 0:
                        session.abort_transaction()
                        raise Exception(f"Requested more items than available stock")
                    
                    productQuery = {"codProduct": productNbr}
                    operation = {"$set": {"stock": newStock}}
                    result = PRODUCTS.update_one(productQuery, operation)
                    if result.matched_count <= 0:
                        session.abort_transaction()
                        raise Exception(f"Billing error")
                session.commit_transaction()
    except Exception as e:
        print(f"Billing error: {e}")
    finally:
        session.end_session()





#============ Getters ==================>


#============ Views ====================>

def createBillDataView():
    """
    Creates a view that groups bills by date.
    """
    try:
        pipeline = [{"$match":{}},
                    {"$project": {
                        "_id":0,
                        "billNbr": 1,
                        "date": 1,
                        "total": 1,
                        "tax": 1,
                        "taxxedTotal": 1,
                        "clientNbr": 1,
                        "details": 1
                    }}]

        mydb.create_collection("billDataByDate", viewOn="bills", pipeline=pipeline)
        view = list(mydb["billDataByDate"].find().sort("date", 1))
        for doc in view:
            if 'date' in doc and isinstance(doc['date'], datetime):
                doc['date'] = doc['date'].strftime("%Y-%m-%d")      #convert datetime to string again
        return view
    except Exception as e:
        print(f"Cannot create view: {e}")

