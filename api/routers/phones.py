from fastapi import APIRouter
from clientService import getAllPhones

router = APIRouter(
  prefix='/phones',
  tags=['phones', 'client_phones']
)

@router.get('/')
async def get_phones():
  return getAllPhones()