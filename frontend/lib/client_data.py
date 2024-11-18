import requests
from crud import find_client_by_id

def get_all_clients_data():
    clients_data = requests.get("http://127.0.0.1:8000/clients/").json()
    return clients_data

def get_telephone_numbers_by_name_and_last_name(name, last_name):
    telephones = requests.get(f"http://127.0.0.1:8000/clients/?name={name}&surname={last_name}").json()
    return telephones

# Returns telephone <> Client data
def get_telephone_client_data():
    telephone_client_data = requests.get("http://127.0.0.1:8000/phones/").json()
    return telephone_client_data

def get_clients_with_at_least_one_bill():
    bills = requests.get("http://127.0.0.1:8000/bills/").json()['data']
    clients_with_bills = []
    for i in range(len(bills)):
        clients_with_bills.append(bills[i]['clientNbr'])

    clients_with_bills = list(set(clients_with_bills)) # To delete duplicates

    client_data = {}
    for client in clients_with_bills:
        client_data[client] = find_client_by_id(client)
    
    return client_data

def get_clients_without_bills():
    bills = requests.get("http://127.0.0.1:8000/bills/").json()['data']
    clients = get_all_clients_data()['data']
    clients_with_bills = [bill['clientNbr'] for bill in bills]

    clients_without_bills = [client for client in clients if client['clientNbr'] not in clients_with_bills]

    return clients_without_bills

# Returns clients <> number of bills
def get_clients_number_of_bills():
    bills = requests.get("http://127.0.0.1:8000/clients/?bills=amount").json()['data']
    ans = {}
    for bill in bills:
        ans[f"{bill['name']} {bill['lastName']}"] = bill['billAmount']
    return ans
