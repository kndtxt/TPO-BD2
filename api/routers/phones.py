from fastapi import APIRouter, status, Response
from services.clientService import getAllPhones
from utils.api_response import response_wrapper

router = APIRouter(
  prefix='/phones',
  tags=['Phones']
)

@router.get('/', status_code=status.HTTP_200_OK)
async def get_phones(response: Response):
  response.status_code = status.HTTP_200_OK
  data = getAllPhones()
  return response_wrapper(data, response)