from fastapi import APIRouter
from services.productService import *
from models import Product

router = APIRouter(
  prefix='/products',
  tags=['Products']
)

@router.get('/{product_id}')
async def get_product_by_id(product_id: int):
  return {'data': getProduct(product_id)}

@router.get('/')
async def get_product(
  brand: str | None = None,
  bought: bool | None = None
):
  by_brand = not isinstance(brand, type(None))
  only_bought = not isinstance(bought, type(None))
  data = []
  if by_brand:
    data = getProductForBrands(brand)
  elif only_bought:
    data = getAllBoughtProducts()
  else:
    data = getAllProducts()
  return {'data': data}

@router.post('/')
async def create_product(product: Product):
  return {'data': insertProduct(product)}

@router.patch('/{product_id}')
async def modify_product(product_id: int, product: Product):
  product.codProduct = product_id
  return {'data': modifyProduct(product)}

@router.post('/not-billed-view')
async def create_not_billed_view():
  return {'data': createProductsNotBilledView()}

@router.delete('/not-billed-view')
async def drop_not_billed_view():
  return {'data': dropProductsNotBilledView()}