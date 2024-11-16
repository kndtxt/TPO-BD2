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
        #update cache
        redis_key = f"product:{product['codProduct']}"     
        c.cache_set(redis_key, product)
        redis_key = f"products:all"
        c.cache_del(redis_key)
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

        #load query to cache
        if product:   
            c.cache_set(redis_key, product)
            product.pop('billNbrs', None) 
            
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
        redis_key = f"products:all"
        cached_products = c.cache_multiple_get(redis_key)
        if cached_products:
            for product in cached_products:
                product.pop('billNbrs', None)
            return cached_products

        products = PRODUCTS.find()

        products_list = list(products)

        #load query to cache
        if products_list:
            redis_key = f"products:all"
            c.cache_set(redis_key, products_list)
            for product in products_list:
                product.pop('billNbrs', None)

        return products_list
    except Exception as e:
        print(f"Error finding all products: {e}")
        return None
    
def getAllProductsWithBillNbrs():
    """
    Searches for all the products in database.
    Returns:
        product list if existent. None otherwise.
    """
    try:
        redis_key = f"products:all"
        cached_products = c.cache_multiple_get(redis_key)
        if cached_products:
            return cached_products

        products = PRODUCTS.find()

        products_list = list(products)

        #load query to cache
        if products_list:
            redis_key = f"products:all"
            c.cache_set(redis_key, products_list)

        return products_list
    except Exception as e:
        print(f"Error finding all products: {e}")
        return None
    
def getAllBoughtProducts():
    """
    Searches for all the products with a non-empty 'billNbr' list (products that have been bought).
    Returns:
        product list if existent. None otherwise.
    """
    try:
        all_products =  getAllProductsWithBillNbrs()
        if all_products:
            all_bought_products = [product for product in all_products if len(product['billNbrs'])>0]
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
        
        #update cache
        redis_key = f"product:{product['codProduct']}"     
        c.cache_set(redis_key, product)
        redis_key = f"products:all"
        c.cache_del(redis_key)
        return True
    except Exception as e:
        print(f"Error modifying product: {e}")
        return False

