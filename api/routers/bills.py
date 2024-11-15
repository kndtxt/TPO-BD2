from fastapi import APIRouter
from billService import *
from api.models import *

router = APIRouter(
  prefix='/bills',
  tags=['bills']
)

@router.post('/')
async def create_bill(bill: Factura): # TODO: modify this since Factura is a class
  return insertBill(bill)