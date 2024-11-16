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