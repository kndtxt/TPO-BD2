import streamlit as st
from lib.crud import create_client, edit_client, delete_client, create_product, edit_product, find_client_by_name_and_last_name

st.title("CRUD")

option = st.selectbox(
    "Create, Update or Delete",
    (
        "Create Client",
        "Edit Client",
        "Delete Client",
        "Create Product",
        "Modify Product",
    ),
)

if option == "Create Client":

    st.subheader("Client Data")

    id = st.number_input("ID", 0)
    name = st.text_input("Name", "John")
    last_name = st.text_input("Last Name", "Doe")
    telephone = st.text_input("Address", "Mulholland Drive")

    st.subheader("Phone Numbers")
    amount_of_phone_numbers = st.number_input("Amount of Phone Numbers", 0)
    phone_numbers = []

    for i in range(amount_of_phone_numbers):
        st.subheader(f"Phone Number {i+1}")

        area_cod = st.text_input(f"Area Code {i+1}", "123")
        number = st.text_input(f"Number {i+1}", "456789")
        type = st.selectbox(f"Type {i+1}", ("M", "F"))

        phone_numbers.append({"areaCod": area_cod, "phoneNbr": number, "phoneType": type})
    
    btn = st.button("Create")
    if btn:
        create_client(id, name, last_name, telephone, phone_numbers)

elif option == "Edit Client":
    st.subheader("Find Client")
    opt = st.selectbox("Find by", ("Name and Last Name", "ID"))

    if opt == "ID":
        st.number_input("ID", 0)
        id_btn = st.button("Search")
    
    else:
        name = st.text_input("Name", "John")
        last_name = st.text_input("Last Name", "Doe")
        find_btn = st.button("Search")

    st.subheader("Client Data")
    # TODO: show data from API in input fields to edit
    name = st.text_input("Name", "")
    last_name = st.text_input("Last Name", "")
    telephone = st.text_input("Address", "")

    btn = st.button("Save")
    if btn:
        pass
        # TODO: Endpoint that edits a client

elif option == "Delete Client":
    st.subheader("Find Client")
    opt = st.selectbox("Find by", ("Name and Last Name", "ID"))

    if opt == "ID":
        id_to_delete = st.number_input("ID", 0)
        id_btn = st.button("Delete")

        if id_btn:
            delete_client(id_to_delete)
    
    else:
        name = st.text_input("Name", "Xerxes")
        last_name = st.text_input("Last Name", "Hale")
        name_btn = st.button("Delete")

        if name_btn:
            name = find_client_by_name_and_last_name(name, last_name)
            # TODO: handle when not found
            delete_client(name['clientNbr'])



elif option == "Create Product":
    name = st.text_input("Name", "Product")
    brand = st.text_input("Brand", "Brand")
    description = st.text_area("Description", "Description")
    price = st.number_input("Price", 0.0)
    btn = st.button("Create")

    if btn:
        pass
        # TODO: Endpoint that creates a product

elif option == "Modify Product":
    st.subheader("Find Product")
    opt = st.selectbox("Find by", ("Name", "ID"))

    if opt == "ID":
        st.number_input("ID", 0)
        find_btn = st.button("Search")

    else:
        name = st.text_input("Name", "Product")
        find_btn = st.button("Search")

    st.subheader("Product Data")

    # TODO: show data from API in input fields to edit
    name = st.text_input("Name", "")
    brand = st.text_input("Brand", "")
    price = st.number_input("Price", 0.0)
    btn = st.button("Edit")

    if btn:
        pass
        # TODO: Endpoint that edits a product

