from fastapi import APIRouter, Query
from typing import Annotated
from services.clientService import getAllClients, getClient, deleteClient
from api.models import *

router = APIRouter(
  prefix='/clients',
  tags=['clients'] 
)


@router.get('/')
async def get_client(name: str | None = None, surname: str | None = None):
  if (isinstance(name, type(None)) or isinstance(surname, type(None))):
    return {'data': getAllClients()}
  else:
    return {'data': getClient(name, surname)}

@router.get('/{client_id}')
async def get_client_by_id(client_id: int):
  return {'data': getClient(client_id)}

@router.delete('/{client_id}')
async def delete_client_by_id(client_id: int):
  return {'data': deleteClient(client_id)}

