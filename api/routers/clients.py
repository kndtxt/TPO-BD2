from fastapi import APIRouter, status, Response
from services.clientService import *
from utils.api_response import response_wrapper
from models import *

router = APIRouter(
  prefix='/clients',
  tags=['Clients'] 
)

@router.get('/', status_code=status.HTTP_200_OK)
async def get_clients(
  response: Response,
  name: str | None = None, 
  surname: str | None = None, 
  bills: str | None = None,
  filter: str | None = None
):
  response.status_code = status.HTTP_200_OK
  by_name_and_surname = not (isinstance(name, type(None)) or isinstance(surname, type(None)))
  by_bills = not isinstance(bills, type(None))
  only_name_surname_with_total_taxes = not isinstance(filter, type(None))
  data = []
  if by_name_and_surname:
    data = getClient(name, surname)
  elif by_bills:
    if bills == 'amount':
      data = getClientsWithBillAmount()
    elif bills == 'any':
      data = getClientsWithBills()
    elif bills == 'none':
      data = getClientsWithNoBills()
    else:
      data = getAllClients()
  elif only_name_surname_with_total_taxes:
    if filter == 'taxes':
      data = getClientTotalWithTaxes()
    else:
      data = getAllClients()
  else:
    data = getAllClients()
  return response_wrapper(data, response)

@router.get('/{client_id}', status_code=status.HTTP_200_OK)
async def get_client_by_id(
  client_id: int,
  response: Response
):
  response.status_code = status.HTTP_200_OK
  data = getClient(client_id)
  return response_wrapper(data, response)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_client(
  client: Client,
  response: Response
):
  response.status_code = status.HTTP_201_CREATED
  data = insertClient(client)
  return response_wrapper(data, response)

@router.patch('/{client_id}', status_code=status.HTTP_200_OK)
async def modify_client(
  client_id: int, 
  client: Client,
  response: Response
):
  response.status_code = status.HTTP_200_OK
  client.clientNbr = client_id
  data = modifyClient(client)
  return response_wrapper(data, response)

@router.delete('/{client_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_by_id(
  client_id: int,
  response: Response
):
  response.status_code = status.HTTP_204_NO_CONTENT
  data = deleteClient(client_id)
  return response_wrapper(data, response)

