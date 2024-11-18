import streamlit as st
from lib.client_data import get_all_clients_data, get_telephone_numbers_by_name_and_last_name, get_telephone_client_data, get_clients_with_at_least_one_bill, get_clients_without_bills, get_clients_number_of_bills

st.title("Clients")

option = st.selectbox(
    "Test the functionality of the Project",
    (
        "Show Client Data", 
        "Show telephone numbers by Name and Last Name", 
        "Show telephone <> client data",
        "Show clients with at least one bill",
        "Show clients without bills",
        "Clients <> Number of bills"
    ),
)

if option == "Show Client Data":
    client_data = get_all_clients_data()['data']
    for client in client_data:
        st.write(f"**ID: {client['clientNbr']} -- Name: {client['name']} {client['lastName']}**") 
        st.write(f"Address: {client['address']}")
        st.write(f"Telephones:")
        for phone in client['phones']:
            st.write(f"{phone['areaCode']} - {phone['phoneNbr']} - {phone['phoneType']}")
        st.write("")    


elif option == "Show telephone numbers by Name and Last Name":
    name = st.text_input("Name", "Jacob")
    last_name = st.text_input("Last Name", "Cooper")
    btn = st.button("Search")

    if btn:
        telephones = get_telephone_numbers_by_name_and_last_name(name, last_name)['data'][0]['phones']
        for telephone in telephones:
            st.write(f"Area code: {telephone['areaCode']} Number: {telephone['phoneNbr']} Type: {telephone['phoneType']}")

elif option == "Show telephone <> client data":
    telephone_data = get_telephone_client_data()['data']
    for telephone in telephone_data:
        st.write("Name: " + telephone['name'] + " " + telephone['lastName'] + " ID: " + str(telephone['clientNbr']))
        st.write(telephone['phone'])
    
elif option == "Show clients with at least one bill":
    data = get_clients_with_at_least_one_bill()
    for client in data:
        st.write(f"ID: {client} -- Name: {data[client]['name']} {data[client]['lastName']}")
    

elif option == "Show clients without bills":
    data = get_clients_without_bills()
    for client in data:
        st.write(f"ID: {client['clientNbr']} -- Name: {client['name']} {client['lastName']}")
        st.write(f"Telephones:")
        for phone in client['phones']:
            st.write(f"{phone['areaCode']} - {phone['phoneNbr']} - {phone['phoneType']}")
        st.write("")

elif option == "Clients <> Number of bills":
    data = get_clients_number_of_bills()
    for client in data:
        st.write(f"Name: {client} -- Number of bills: {data[client]}")
