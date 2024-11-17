from fastapi import APIRouter, status, Response
from services.productService import *
from models import Product
from utils.api_response import response_wrapper

router = APIRouter(
  prefix='/products',
  tags=['Products']
)

@router.get('/{product_id}', status_code=status.HTTP_200_OK)
async def get_product_by_id(
  response: Response,
  product_id: int
):
  response.status_code = status.HTTP_200_OK
  data = getProduct(product_id)
  return response_wrapper(data, response)

@router.get('/', status_code=status.HTTP_200_OK)
async def get_product(
  response: Response,
  brand: str | None = None,
  bought: bool | None = None
):
  response.status_code = status.HTTP_200_OK
  by_brand = not isinstance(brand, type(None))
  only_bought = not isinstance(bought, type(None))
  data = []
  if by_brand:
    data = getProductForBrands(brand)
  elif only_bought:
    data = getAllBoughtProducts()
  else:
    data = getAllProducts()
  return response_wrapper(data, response)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(
  product: Product,
  response: Response
):
  response.status_code = status.HTTP_201_CREATED
  data = insertProduct(product)
  return response_wrapper(data, response)

@router.patch('/{product_id}', status_code=status.HTTP_200_OK)
async def modify_product(
  product_id: int, 
  product: Product,
  response: Response,
):
  response.status_code = status.HTTP_200_OK
  product.codProduct = product_id
  data = modifyProduct(product)
  return response_wrapper(data, response)

@router.post('/not-billed-view', status_code=status.HTTP_201_CREATED)
async def create_not_billed_view(response: Response):
  response.status_code = status.HTTP_201_CREATED
  data = createProductsNotBilledView()
  return response_wrapper(data, response)

@router.delete('/not-billed-view', status_code=status.HTTP_204_NO_CONTENT)
async def drop_not_billed_view(response: Response):
  response.status_code = status.HTTP_204_NO_CONTENT
  data = dropProductsNotBilledView()
  return response_wrapper(data, response)
