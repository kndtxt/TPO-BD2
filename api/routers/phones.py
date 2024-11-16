from fastapi import APIRouter
from services.clientService import getAllPhones

router = APIRouter(
  prefix='/phones',
  tags=['Phones']
)

@router.get('/')
async def get_phones():
  return {'data': getAllPhones()}