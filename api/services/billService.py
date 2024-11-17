#============ Imports ==================>
from persistence.persistence import mydb, mongoClient, BILLS, CLIENTS, PRODUCTS
from .productService import getProduct, getProductForBrands
from .clientService import getClient
import persistence.cache as c
from models import Bill
from utils.json_serialize_utils import clean_data
from datetime import datetime
from utils.api_response import ResponseStatus
from fastapi import status
from pymongo.errors import CollectionInvalid

#session to allow transactional behaviour


#============ Setters ==================>
def insertBill(bill: Bill): 
    '''
    Populates db with provided dataset. Assumes stocks need not be updated.
    Args:
        bill(Bill): the bill to be inserted
    '''
    try:
        bill_data = bill.model_dump()
        clientNbr = int(bill_data['clientNbr'])
        clientQuery = {'clientNbr': clientNbr}
        operation = {'$push': {'billNbrs': bill_data['billNbr']}}
        updateClient = CLIENTS.update_one(clientQuery, operation)  # add reference to bill that client has purchased
        if updateClient.matched_count <= 0:
            return ResponseStatus(status.HTTP_404_NOT_FOUND, 'Client for bill not found.')
        
        for detail in bill_data['details']:
            codProduct = int(detail['codProduct'])
            productQuery = {'codProduct': codProduct}
            updateProduct = PRODUCTS.update_one(productQuery, operation)  # add reference to bill where product was billed
            if updateProduct.matched_count <= 0:
                return ResponseStatus(status.HTTP_404_NOT_FOUND, 'Product for bill not found.')

        newBill = BILLS.insert_one(bill_data)
        return newBill
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')

def insertNewBill(bill: Bill):
    '''
    Insert given bill into db and updates product stock with transactional behaviour.
    Args:
        bill(Bill): the bill to be inserted
    Returns:
        Bill if inserted. None otherwise.
    '''
    try:
        with mongoClient.start_session() as session:
            with session.start_transaction():
                insertBill(bill)
                bill_data = bill.model_dump()
                for detail in bill_data['details']:
                    productNbr = detail['codProduct']
                    product = getProduct(productNbr)
                    
                    if product is None:
                        session.abort_transaction()
                        return ResponseStatus(status.HTTP_404_NOT_FOUND, 'Product for bill not found.')
                    
                    newStock = product['stock'] - detail['amount']
                    if newStock < 0:
                        session.abort_transaction()
                        return ResponseStatus(status.HTTP_400_BAD_REQUEST, 'Requested more items than available stock')
                    
                    productQuery = {'codProduct': productNbr}
                    operation = {'$set': {'stock': newStock}}
                    result = PRODUCTS.update_one(productQuery, operation)
                    if result.matched_count <= 0:
                        session.abort_transaction()
                        return ResponseStatus(status.HTTP_412_PRECONDITION_FAILED, 'Billing error')
                session.commit_transaction()
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')
    finally:
        session.end_session()

#============ Getters ==================>

def getAllBills():
    '''
    Searches for all the bills in database.
    Caches query afterwards.

    Returns:
        bill list if existent. None otherwise.
    '''
    try:
        redis_key = 'bills:all'
        cached_bills = c.cache_get(redis_key)
        if cached_bills:
            return cached_bills
        
        bills = clean_data(BILLS.find())

        if len(bills) > 0:
            c.cache_set(redis_key, bills)

        return bills
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')
    
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
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')

def getBill(billNbr: int):
    '''
    Searches for a specific bill

    Args:
        int: the bill number
    
    Returns:
        bill with that number
    '''
    try:
        redis_key = f'bills:{billNbr}'
        cached_bill = c.cache_get(redis_key)
        if cached_bill:
            return cached_bill
        
        query = {'billNbr': billNbr}
        projection = {'_id': 0}
        bill = clean_data(BILLS.find(query, projection))

        if len(bill) > 0:
            c.cache_set(redis_key, bill)

        return bill
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')
    
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
            return ResponseStatus(status.HTTP_404_NOT_FOUND, 'No clients with that name were found.')

        clientNbrs = [c['clientNbr'] for c in maybe_clients]
        query = {'clientNbr': {'$in': clientNbrs}}
        projection = {'_id': 0, }
        bill_list = clean_data(BILLS.find(query, projection))
        if bill_list:
            c.cache_set(redis_key, bill_list)

        return bill_list
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')



#============ Views ====================>

def createBillDataView():
    '''
    Creates a view that groups bills by date.
    '''
    try:
        pipeline = [
            {
                '$match':{}
            },
            {
                '$project': {
                    '_id':0,
                    'billNbr': 1,
                    'date': 1,
                    'total': 1,
                    'tax': 1,
                    'taxxedTotal': 1,
                    'clientNbr': 1,
                    'details': 1
                }
            },
            {
                '$sort': {
                    'date': 1
                }
            }
        ]

        mydb.create_collection('billDataByDate', viewOn='bills', pipeline=pipeline)
        view = clean_data(mydb['billDataByDate'].find())
        return view
    except CollectionInvalid as e:
        return ResponseStatus(status.HTTP_409_CONFLICT, f'Invalid collection: {e}')
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')

def dropBillDataView():
    '''
    Drops the view that groups bills by date.
    '''
    try:
        mydb.drop_collection('billDataByDate')
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')
    return True
