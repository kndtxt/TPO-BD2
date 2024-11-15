from fastapi import APIRouter
from productService import *
from api.models import *

router = APIRouter(
  prefix='/products',
  tags=['products']
)

@router.get('/{product_id}')
async def get_product_by_id(product_id: int):
  return getProduct(product_id)

@router.post('/')
async def create_product(product: Producto): # TODO: modify this since Producto is a class
  return insertProduct(product)
