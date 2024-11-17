from fastapi import APIRouter, status, Response
from services.billService import *
from models import *
from utils.api_response import response_wrapper

router = APIRouter(
  prefix='/bills',
  tags=['Bills']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_bill(
  bill: Bill,
  response: Response
):
  response.status_code = status.HTTP_201_CREATED
  data = insertNewBill(bill)
  return response_wrapper(data, response)

@router.get('/', status_code=status.HTTP_200_OK)
async def get_bills(
  response: Response,
  name: str | None = None, 
  surname: str | None = None, 
  brand: str | None = None
):
  response.status_code = status.HTTP_200_OK
  by_name_and_surname = not (isinstance(name, type(None)) or isinstance(surname, type(None)))
  by_brand = not isinstance(brand,type(None))
  data = []
  if (by_name_and_surname):
    data = getBills(name, surname)
  if (by_brand):
    data = getBillsByBrand(brand)
  else:
    data = getAllBills()
  return response_wrapper(data, response)

@router.get('/{bill_id}', status_code=status.HTTP_200_OK)
async def get_bill_by_id(
  bill_id: int,
  response: Response
):
  response.status_code = status.HTTP_200_OK
  data = getBill(bill_id)
  return response_wrapper(data, response)

@router.post('/date-view', status_code=status.HTTP_201_CREATED)
async def create_bills_by_date_view(response: Response):
  response.status_code = status.HTTP_201_CREATED
  data = createBillDataView()
  return response_wrapper(data, response)

@router.delete('/date-view', status_code=status.HTTP_204_NO_CONTENT)
async def drop_bills_by_date_view(response: Response):
  response.status_code = status.HTTP_204_NO_CONTENT
  data = dropBillDataView()
  return response_wrapper(data, response)
