from fastapi import APIRouter
from services.productService import *
from models import Product

router = APIRouter(
  prefix='/products',
  tags=['products']
)

@router.get('/{product_id}')
async def get_product_by_id(product_id: int):
  return {'data': getProduct(product_id)}

@router.post('/')
async def create_product(product: Product):
  return {'data': insertProduct(product)}
