import requests
from .crud import find_client_by_id

def get_name_and_last_name_amount_of_bills():
    bills = requests.get("http://127.0.0.1:8000/bills/").json()['data']
    client_data = {}
    for bill in bills:
        client = find_client_by_id(bill['clientNbr'])
        if client == []:
            continue
        else: 
            full_name = f"{client['name']} {client['lastName']}"
            
            if full_name in client_data:
                client_data[full_name] += 1
            else:
                client_data[full_name] = 1
    
    return client_data

# TODO: Check endpoint
def get_bills_by_name_and_last_name(name, last_name):
    response = requests.get(f"http://127.0.0.1:8000/bills/?name={name}&surname={last_name}").json()
    return response

def get_bills_with_products_from_brand(brand):
    response = requests.get(f"http://127.0.0.1:8000/bills/?brand={brand}").json()   
    return response['data']   

# Returns Name, Last Name <> Spent
def get_name_last_name_money_spent():
    bills = requests.get("http://127.0.0.1:8000/bills/").json()['data']
    client_data = {}
    for bill in bills:
        client = find_client_by_id(bill['clientNbr'])
        if client == []:
            continue
        else: 
            full_name = f"{client['name']} {client['lastName']}"
            
            if full_name in client_data:
                client_data[full_name] += bill['taxxedTotal']
            else:
                client_data[full_name] = bill['taxxedTotal']
    
    return client_data

def get_bill_data_ordered_by_dates():
    delete = requests.delete("http://127.0.0.1:8000/bills/date-view")
    response = requests.post("http://127.0.0.1:8000/bills/date-view").json()
    return response

# TODO: check endpoint
def get_products_not_billed():
    delete = requests.delete("http://127.0.0.1:8000/products/not-billed-view")
    response = requests.post("http://127.0.0.1:8000/products/not-billed-view").json()
    return response

# TODO: check endpoint
def get_products_billed_at_least_once():
    products = requests.get("http://127.0.0.1:8000/products/?bought=true").json()
    return products['data']
