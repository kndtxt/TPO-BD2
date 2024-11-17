from fastapi import APIRouter
from services.billService import *
from models import *
from utils.api_response import response

router = APIRouter(
  prefix='/bills',
  tags=['Bills']
)

@router.post('/')
async def create_bill(bill: Bill): 
  data = insertNewBill(bill)
  return response(data)

@router.get('/')
async def get_bill(name: str | None = None, surname: str | None = None, brand: str | None = None):
  by_name_and_surname = not (isinstance(name, type(None)) or isinstance(surname, type(None)))
  by_brand = not isinstance(brand,type(None))
  data = []
  if (by_name_and_surname):
    data = getBills(name, surname)
  if (by_brand):
    data = getBillsByBrand(brand)
  else:
    data = getAllBills()
  return response(data)

@router.post('/date-view')
async def create_bills_by_date_view():
  data = createBillDataView()
  return response(data)

@router.delete('/date-view')
async def drop_bills_by_date_view():
  data = dropBillDataView()
  return response(data)
