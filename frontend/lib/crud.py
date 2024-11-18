import requests

# TODO: Handle when not found 

def find_client_by_id(id):
    client = requests.get(f"http://127.0.0.1:8000/clients/{id}").json()['data']
    return client    

def find_client_by_name_and_last_name(name, last_name):
    client = requests.get(f"http://127.0.0.1:8000/clients/?name={name}&surname={last_name}").json()['data'][0]
    return client

def find_product_by_id(id):
    product = requests.get(f"http://127.0.0.1:8000/products/{id}").json()['data']
    return product

def create_client(id, name, last_name, address, telephones):
    body = {
        "clientNbr": id,
        "name": name,
        "lastName": last_name,
        "address": address,
        "active": 63,
        "phones": telephones,
        "billNbrs": []
    }
    try:
        response = requests.post("http://127.0.0.1:8000/clients/", json=body)
        response.raise_for_status()
        data = response.json()
        
        if ('detail' in data):
            return data['detail'][0]['msg']
        return True
    except requests.exceptions.RequestException as e:
        return f"Error creating client: {str(e)}"


def edit_client(id, name, last_name, address, telephones):
    bills = requests.get("http://127.0.0.1:8000/bills/").json()['data']
    client_bills = []
    for bill in bills:
        if bill['clientNbr'] == id:
            client_bills.append(bill['billNbr'])
    
    active = find_client_by_id(id)['active']
    body = {
        "clientNbr": id,
        "name": name,
        "lastName": last_name,
        "address": address,
        "active": active,
        "phones": telephones,
        "billNbrs": client_bills
    }
    response = requests.patch(f"http://127.0.0.1:8000/clients/{id}", json=body).json()

def delete_client(id):
    response = requests.delete(f"http://127.0.0.1:8000/clients/{id}").json()
    return response
    

def create_product(id, name, brand, description, price, stock):
    body = {
        "codProduct": id,
        "brand": brand,
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "billNbrs": [
            0
        ]
    }

    response = requests.post("http://127.0.0.1:8000/products", json=body).json()

    if ('detail' in response.keys()):
        return response['detail'][0]['msg']
    else:
        return True # Created

def edit_product(id, name, brand, description, price, stock):
    body = {
        "codProduct": id,
        "brand": brand,
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
    }
    response = requests.patch(f"http://127.0.0.1:8000/products/{id}", json=body).json()

