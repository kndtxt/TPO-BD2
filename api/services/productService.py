#============ Imports ==================>
from persistence.persistence import mydb, PRODUCTS
import persistence.cache as c
from models import Product
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError
from functools import singledispatch

#============ Setters ==================>
def insertProduct(product: Product):
    """
    Inserts product into database.
    Args:
        product dictionary, according the Product model

    Returns:
        product if created. None otherwise.
    """ 
    try:
        product = product.model_dump()
        newProduct = PRODUCTS.insert_one(product)

        #update cache
        redis_key = f"product:{product['codProduct']}"
        c.cache_set(redis_key, product)
        redis_key = f"products:all"
        c.cache_del(redis_key)

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
            cached_prod.pop('billNbrs', None)
            cached_prod.pop('_id', None)
            return cached_prod

        query = {"codProduct": codProd}
        product = PRODUCTS.find_one(query)

        if product:        
            c.cache_set(redis_key, product)
            product.pop('billNbrs', None)
            product.pop('_id', None)
            
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
                product.pop('_id', None)
            return cached_products

        products = PRODUCTS.find()

        products_list = list(products)

        #load query to cache
        if products_list:
            redis_key = f"products:all"
            c.cache_set(redis_key, products_list)
            for product in products_list:
                product.pop('billNbrs', None)
                product.pop('_id', None)

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
            for product in cached_products:
                product.pop('_id', None)
            return cached_products

        products = PRODUCTS.find()

        products_list = list(products)

        #load query to cache
        if products_list:
            redis_key = f"products:all"
            c.cache_set(redis_key, products_list)
            for product in products_list:
                product.pop('_id', None)

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
def modifyProduct(product: Product):
    """
    Modifies a persisted product.
    Args:
        product(Product): the product to be modified
    Returns:
        True if modified. False otherwise
    """
    try:
        product = product.model_dump()
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
        
        #update cache
        redis_key = f"product:{product['codProduct']}"
        c.cache_set(redis_key, product)
        redis_key = f"products:all"
        c.cache_del(redis_key)

        return True
    except Exception as e:
        print(f"Error modifying product: {e}")
        return False


# ============ Views ====================>

def createProductsNotBilledView():
    """
    Creates a view of products that were not billed yet. 
    """
    try:
        pipeline = [{"$match":{"billNbrs":{"$size":0}}},    #products that were not billed yet
                    {"$project": {
                        "_id":0,
                        "codProduct": 1,
                        "brand": 1,
                        "name": 1,
                        "description": 1,
                        "price": 1,
                        "stock": 1               
                    }}]

        mydb.create_collection("notBilledProducts", viewOn="products", pipeline=pipeline)
        view = mydb["notBilledProducts"].find().sort("date", 1)
        return view
    except Exception as e:
        print(f"Error creating view: {e}")
        return None