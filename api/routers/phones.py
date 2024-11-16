from fastapi import APIRouter
from services.clientService import getAllPhones

router = APIRouter(
  prefix='/phones',
  tags=['phones']
)

@router.get('/')
async def get_phones():
  return {'data': getAllPhones()}