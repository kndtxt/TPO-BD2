import requests

def get_all_clients_data():
    clients_data = requests.get("http://127.0.0.1:8000/clients/").json()
    return clients_data

def get_telephone_numbers_by_name_and_last_name(name, last_name):
    telephones = requests.get(f"http://127.0.0.1:8000/clients/?name={name}&surname={last_name}").json()
    # TODO: show only ID and telephones
    return telephones

# Returns telephone <> Client data
def get_telephone_client_data():
    telephone_client_data = requests.get("http://127.0.0.1:8000/phones/").json()
    return telephone_client_data

def get_clients_with_at_least_one_bill():
    pass

def get_clients_without_bills():
    pass

# Returns clients <> number of bills
def get_clients_number_of_bills():
    pass
