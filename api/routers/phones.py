from fastapi import APIRouter
import sys, os
sys.path.append(os.getcwd())
from clientService import getAllPhones

router = APIRouter(
  prefix='/phones',
  tags=['phones']
)

@router.get('/')
async def get_phones():
  return getAllPhones()