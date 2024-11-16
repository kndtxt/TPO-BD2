#============ Imports ==================>
from persistence import PRODUCTS
import cache as c
from pydantic import ValidationError

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
        result = PRODUCTS.insert_one(product)
        newProduct = PRODUCTS.find_one({"_id": result.inserted_id})
        redis_key = f"product:{newProduct['codProduct']}"     #load to cache
        c.cache_set(redis_key, newProduct)
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
            cached_prod.pop('billNbrs', None)
            return cached_prod

        query = {"codProduct": codProd}
        product = PRODUCTS.find_one(query)

        if product:
            product.pop('billNbrs', None)    
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
        cached_products = c.cache_multiple_get(redis_key)

        if cached_products:
            for product in cached_products:
                product.pop('billNbrs', None)

        return cached_products
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
            all_bought_products = [product for product in all_products if 'billNbrs' in product and product['billNbrs']]
            for product in all_bought_products:
                product.pop('billNbrs', None)
            return all_bought_products
        
        else:
            return None
    except Exception as e:
        print(f"Error finding all products: {e}")
        return None
    
#============ Modify ===========>
def modifyProduct(product):
    """
    Modifies a persisted product. Must have the corresponding codProduct in it.
    Args:
        product(Product): the product to be modified
    Returns:
        True if modified. False otherwise.
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
        
        redis_key = f"product:{product['codProduct']}"     #load to cache
        c.cache_set(redis_key, product)
        return True
    except Exception as e:
        print(f"Error modifying product: {e}")
        return False

