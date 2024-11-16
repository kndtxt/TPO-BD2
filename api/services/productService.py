#============ Imports ==================>
from api.persistence.persistence import mydb, PRODUCTS
import api.persistence.cache as c
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


# ============ Views ====================>

def createProductsNotBilledView():
    """
    Creates a view of products that were not billed yet. 
    """
    try:
        pipeline = [{"$match":{"billNbrs":{"$size":0}}},    #products that were not billed yet
                    {"$project": {
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