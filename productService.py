#============ Imports ==================>
from persistence import mydb
import cache as c
from models import Producto
from pydantic import ValidationError
from functools import singledispatch

#============ Dbs Connection ===========>
PRODUCTS = mydb["clients"]
PRODUCTS.create_index([('codProduct', 1)], unique=True)

#============ Setters ==================>
def insertProduct(product):
    """
    Inserts product into database.

    Args:
        product dictionary, according the Product model

    Returns:
        product if created. None otherwise.
    """ 
    try:
        codProduct = int(product['codProduct']) if isinstance(product['codProduct'], str) else product['codProduct']
        query = {"codProduct": codProduct}
        aux_prod = PRODUCTS.find_one(query)
        if aux_prod is not None:
            print(f"Product for codProduct: {codProduct} already exists!")
            return None

        aux_prod = Producto(**product)#validate by model
        newProduct = PRODUCTS.insert_one(aux_prod.dict())
        return newProduct
    except ValidationError as e:
        print(f"Data validation error: {e}")
    except Exception as e:
        print(e)
        return None

#============ Getters ==================>
def getProduct(codProd: int):
    """
    Searches for the product with the given codProd in database.
    Uses redis caching.

    Args:
        int: the product key.

    Returns:
        product if existent. None otherwise.
    """
    try:
        redis_key = f"product:{codProd}"     #first search in cached data
        cached_client = c.cache_get(redis_key)
        if cached_client:
            return cached_client

        query = {"codProduct": codProd}
        product = PRODUCTS.find_one(query)

        if product:        
            c.cache_set(redis_key, product)
            
        return product
    except Exception as e:
        print(f"Error finding product: {e}")
        return None
            