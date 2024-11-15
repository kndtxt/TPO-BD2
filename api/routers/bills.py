from fastapi import APIRouter
import sys, os
sys.path.append(os.getcwd())
from billService import *
from models import *

router = APIRouter(
  prefix='/bills',
  tags=['bills']
)

@router.post('/')
async def create_bill(bill: Bill): 
  return insertBill(bill)