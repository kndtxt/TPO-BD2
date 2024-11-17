from fastapi import APIRouter
from services.clientService import *
from models import *

router = APIRouter(
  prefix='/clients',
  tags=['Clients'] 
)

@router.get('/')
async def get_client(
  name: str | None = None, 
  surname: str | None = None, 
  bills: str | None = None,
  filter: str | None = None
):
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
  return {'data': data}

@router.get('/{client_id}')
async def get_client_by_id(client_id: int):
  return {'data': getClient(client_id)}

@router.post('/')
async def create_client(client: Client):
  return {'data': insertClient(client)}

@router.patch('/{client_id}')
async def modify_client(client_id: int, client: Client):
  client.clientNbr = client_id
  return {'data': modifyClient(client)}

@router.delete('/{client_id}')
async def delete_client_by_id(client_id: int):
  return {'data': deleteClient(client_id)}

