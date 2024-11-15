from fastapi import APIRouter
from clientService import getAllClients, getClient, deleteClient
from api.models import *

router = APIRouter(
  prefix='/clients',
  tags=['clients']
)

@router.get('/')
async def get_clients():
  return getAllClients()

@router.get('/') # TODO: fix same endpoint
async def get_client_by_name_and_surname(body: NameAndSurname):
  [name, surname] = body
  return getClient(name, surname)

@router.get('/{client_id}')
async def get_client_by_id(client_id: int):
  return getClient(client_id)

@router.delete('/{client_id}')
async def delete_client_by_id(client_id: int):
  return deleteClient(client_id)

