#============ Imports ==================>
from api.persistence.persistence import mydb, mongoClient, session, BILLS, CLIENTS, PRODUCTS
from .productService import getProduct, getProductForBrands
from .clientService import getClient
import api.persistence.cache as c
from models import Bill
from pydantic import ValidationError
from functools import singledispatch
from bson import json_util
from utils.json_serialize_utils import clean_data
import json

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

def getAllBills():
    '''
    Searches for all the bills in database.
    Caches query afterwards.

    Returns:
        bill list if existent. None otherwise.
    '''
    try:
        redis_key = f'bills:all'
        cached_bills = c.cache_get(redis_key)
        if cached_bills:
            return cached_bills
        
        bills = clean_data(BILLS.find())

        if len(bills) > 0:
            c.cache_set(redis_key, bills)

        return bills
    except Exception as e:
        print(f'Error finding all the bills: {e}')
        return None
    
def getBillsByBrand(brand: str):
    '''
    Searches for the bills for a product with a specific brand name.
    Uses redis caching.

    Args:
        str: the product brand name

    Returns:
        bills for products with a specific brand name
    '''
    try:
        redis_key = f'bills:product_brand:{brand}'
        cached_bills = c.cache_get(redis_key)
        if cached_bills:
            return cached_bills
        
        products = getProductForBrands(brand)
        product_ids = [p['codProduct'] for p in products]
        query = {'details.codProduct': {'$in': product_ids}}
        bills = clean_data(BILLS.find(query))
        if len(bills) > 0:
            c.cache_set(redis_key, bills)
        return bills
    except Exception as e:
        print(f"Error finding bills: {e}")
        return None
    
def getBills(name: str, surname: str):
    '''
    Searches for the bills bought by a client given it's name and surname in database.
    Uses redis caching.
    
    Args:
        str: the client name.
        str: the client surname.

    Returns:
        bills bought by the client if existent. None otherwise.
    ''' 
    try:
        redis_key = f'bills:{name}:{surname}'
        cached_bills = c.cache_get(redis_key)
        if cached_bills:
            return cached_bills
        
        maybe_clients = getClient(name, surname)
        if isinstance(maybe_clients, type(None)):
            return None

        clientNbrs = [c['clientNbr'] for c in maybe_clients]
        query = {'clientNbr': {'$in': clientNbrs}}
        bill_list = list(BILLS.find(query))

        if bill_list:
            c.cache_set(redis_key, bill_list)

        return bill_list
    except Exception as e:
        print(f'Error finding bills bought by that client: {e}')
        return None

