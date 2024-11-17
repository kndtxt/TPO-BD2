#============ Imports ==================>
from persistence.persistence import mydb, PRODUCTS
import persistence.cache as c
from models import Product
from pymongo.errors import DuplicateKeyError
from functools import singledispatch
from utils.json_serialize_utils import clean_data
import json
from fastapi import status
from utils.api_response import ResponseStatus
from pymongo.errors import CollectionInvalid

#============ Setters ==================>
def insertProduct(product: Product):
    '''
    Inserts product into database.
    Args:
        product dictionary, according the Product model

    Returns:
        product if created. None otherwise.
    ''' 
    try:
        product = product.model_dump()
        newProduct = PRODUCTS.insert_one(product)

        #update cache
        codProduct = product['codProduct']
        redis_key = f'product:{codProduct}'
        c.cache_set(redis_key, product)
        redis_key = 'products:all'
        c.cache_del(redis_key)

        return {'_id': str(newProduct.inserted_id)}
    except DuplicateKeyError as e:
        codProduct = product['codProduct']
        return ResponseStatus(status.HTTP_422_UNPROCESSABLE_ENTITY, f'Product for codProduct: {codProduct} already exists.')
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')


#============ Getters ==================>
def getProduct(codProd: int):
    '''
    Searches for the product with the given codProd in database.
    Uses redis caching.
    Args:
        int: the product key.
    Returns:
        product if existent. None otherwise.
    '''
    try:
        redis_key = f'product:{codProd}'     #first search in cached data
        cached_prod = c.cache_get(redis_key)
        if cached_prod:
            cached_prod.pop('billNbrs', None)
            return cached_prod

        query = {'codProduct': codProd}
        projection = {'_id': 0}
        product = PRODUCTS.find_one(query, projection)

        if product:        
            c.cache_set(redis_key, product)
            product.pop('billNbrs', None)
            
        return product
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')

            
def getProductForBrands(brand: str):
    '''
    Searches for the products with a specific brand name
    Uses redis caching.

    Args:
        str: the brand name

    Returns:
        products with a specific brand name. None otherwise.
    '''
    try:
        redis_key = f'product:brand:{brand}'
        cached_products = c.cache_get(redis_key)
        if cached_products:
            return cached_products
        
        query = {'brand': {'$regex': brand}}
        products = clean_data(PRODUCTS.find(query))
        if len(products) > 0:        
            c.cache_set(redis_key, products)
            
        return products
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')
    

def getAllProducts():
    '''
    Searches for all the products in database.
    Returns:
        product list if existent. None otherwise.
    '''
    try:
        redis_key = 'products:all'
        cached_products = c.cache_multiple_get(redis_key)
        if cached_products and len(cached_products) > 0:
            for product in cached_products:
                product.pop('billNbrs', None)
            return cached_products

        projection = {'_id': 0}
        products = clean_data(PRODUCTS.find({}, projection))

        #load query to cache
        if len(products) > 0:
            redis_key = 'products:all'
            c.cache_set(redis_key, products)
            for product in products:
                product.pop('billNbrs', None)

        return products
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')


def getAllProductsWithBillNbrs():
    '''
    Searches for all the products in database.
    Returns:
        product list if existent. None otherwise.
    '''
    try:
        redis_key = 'products:all'
        cached_products = c.cache_get(redis_key)
        if cached_products:
            for product in cached_products:
                product.pop('_id', None)
            return cached_products

        projection = {'_id': 0}
        products = clean_data(PRODUCTS.find({}, projection))

        #load query to cache
        if products:
            redis_key = 'products:all'
            c.cache_set(redis_key, products)

        return products
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')

    
def getAllBoughtProducts():
    '''
    Searches for all the products with a non-empty 'billNbr' list (products that have been bought).
    Returns:
        product list if existent. None otherwise.
    '''
    try:
        all_products =  getAllProductsWithBillNbrs()
        if all_products:
            all_bought_products = [product for product in all_products if 'billNbrs' in product and len(product['billNbrs']) > 0]
            for product in all_bought_products:
                product.pop('billNbrs', None)
            return all_bought_products
        else:
            return None
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')


#============ Modify ===========>
def modifyProduct(product: Product):
    '''
    Modifies a persisted product.
    Args:
        product(Product): the product to be modified
    Returns:
        True if modified. False otherwise
    '''
    try:
        product = product.model_dump()
        codProduct = product['codProduct']
        filter = {'codProduct': codProduct}
        fields = {}
        for key, value in product.items():
            if key != '_id' and key != 'productNbr':
                fields[key] = value
        operation = {'$set': fields}
        result = PRODUCTS.update_one(filter, operation)
        if result.modified_count <=0: 
            raise Exception('No products modified')
        
        #update cache
        redis_key = f'product:{codProduct}'
        c.cache_set(redis_key, product)
        redis_key = 'products:all'
        c.cache_del(redis_key)

        return True
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')



# ============ Views ====================>

def createProductsNotBilledView():
    '''
    Creates a view of products that were not billed yet. 
    '''
    try:
        pipeline = [
            {
                '$match': {
                    'billNbrs':{
                        '$size': 0  #products that were not billed yet
                    } 
                } 
            },    
            {
                '$project': {
                    '_id':0,
                    'codProduct': 1,
                    'brand': 1,
                    'name': 1,
                    'description': 1,
                    'price': 1,
                    'stock': 1               
                }
            }
        ]

        mydb.create_collection('notBilledProducts', viewOn='products', pipeline=pipeline)
        view = clean_data(mydb['notBilledProducts'].find())
        return view
    except CollectionInvalid as e:
        return ResponseStatus(status.HTTP_409_CONFLICT, f'Invalid collection: {e}')
    except Exception as e:
        return ResponseStatus(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Internal server error: {e}')

    
def dropProductsNotBilledView():
    '''
    Drops a view of products that were not billed yet. 
    '''
    mydb.drop_collection('notBilledProducts')
    return True