from fastapi import APIRouter
from services.clientService import getAllPhones
from utils.api_response import response

router = APIRouter(
  prefix='/phones',
  tags=['Phones']
)

@router.get('/')
async def get_phones():
  data = getAllPhones()
  return response(data)