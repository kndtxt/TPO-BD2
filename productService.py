#============ Imports ==================>
from persistence import mydb, PRODUCTS
import cache as c
import models
from pydantic import ValidationError
from functools import singledispatch

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
        query = {"codProduct": product['codProduct']}
        aux_prod = PRODUCTS.find_one(query)
        if aux_prod is not None:
            print(f"Product for codProduct: {product['codProduct']} already exists!")
            return None

        aux_prod = Product(**product)#validate by model
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
        cached_prod = c.cache_get(redis_key)
        if cached_prod:
            return cached_prod

        query = {"codProduct": codProd}
        product = PRODUCTS.find_one(query)

        if product:        
            c.cache_set(redis_key, product)
            
        return product
    except Exception as e:
        print(f"Error finding product: {e}")
        return None
            

#============ Modify ===========>
def modifyProduct(product):
    """
    Modifies a persisted product.
    Args:
        product(Product): the product to be modified
    Returns:
        True if modified. False otherwise
    """
    try:
        filter = {"codProduct": product['codProduct']}
        fields = {}
        for key, value in product.items():
            if key != "_id" and key != "productNbr":
                fields[key] = value
        operation = {"$set": fields}
        result = PRODUCTS.update_one(filter, operation)
        if result.modified_count <=0: 
            raise Exception("No products modified")
            return False
        
        #TODO modify cache here!!!!!!!!!!!
        return True
    except Exception as e:
        print(f"Error modifying product: {e}")
        return False

