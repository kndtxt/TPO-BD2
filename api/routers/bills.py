from fastapi import APIRouter
from services.billService import *
from models import *

router = APIRouter(
  prefix='/bills',
  tags=['Bills']
)

@router.post('/')
async def create_bill(bill: Bill): 
  return {'data': insertBill(bill)}

@router.get('/')
async def get_bill(name: str | None = None, surname: str | None = None, brand: str | None = None):
  if (not isinstance(name, type(None)) and not isinstance(surname, type(None))):
    return {'data': getBills(name, surname)}
  if (not isinstance(brand, type(None))):
    return {'data': getBillsByBrand(brand)}
  else:
    return {'data': getAllBills()}
