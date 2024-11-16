#============ Imports ==================>
from api.persistence.persistence import PRODUCTS
import api.persistence.cache as c
from models import Product
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

#============ Setters ==================>
def insertProduct(product: Product):
    """
    Inserts product into database.

    Args:
        product dictionary, according the Product model

    Returns:
        product if created. None otherwise.
    """ 
    try:#TODO guardar en cache despues de mongo
        newProduct = PRODUCTS.insert_one(product.model_dump())
        return str(newProduct.inserted_id)
    except ValidationError as e:
        print(f"Data validation error: {e}")
    except DuplicateKeyError as e:
        print(f"Product for codProduct: {product['codProduct']} already exists!")
        return None
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
            
def getAllProducts():
    """
    Searches for all the products in database.

    Returns:
        product list if existent. None otherwise.
    """
    try:
        redis_key = f"product:*"#TODO si esto funca ayuda a no tener que borrar el "all", solo modificar o borrar auqells q si
        return c.cache_multiple_get(redis_key)

    except Exception as e:
        print(f"Error finding all products: {e}")
        return None

def getAllBoughtProducts():
    """
    Searches for all the products with a non-empty 'billNbr' list (products that have been bought).
    Caches query afterwards.

    Returns:
        product list if existent. None otherwise.
    """
    try:
        redis_key = f"product:*"#TODO si esto funca ayuda a no tener que borrar el "all", solo modificar o borrar auqells q si
        all_products =  c.cache_multiple_get(redis_key)

        if all_products:
            all_bought_products = [product for product in all_products if 'billNbr' in product and product['billNbr']]
            return all_bought_products
        
        else:
            return None

    except Exception as e:
        print(f"Error finding all products: {e}")
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
        
        #TODO modify cache here!!!!!!!!!!!
        if result:    #caching
            redis_key = f"product:{product['codProduct']}"
            c.cache_set(redis_key, result)
        return True
    except Exception as e:
        print(f"Error modifying product: {e}")
        return False

