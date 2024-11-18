import streamlit as st
from lib.crud import create_client, edit_client, delete_client, create_product, edit_product, find_client_by_id, find_client_by_name_and_last_name, find_product_by_id

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
        st.success("Client created successfully.")
        
elif option == "Edit Client":
    st.subheader("Find Client")
    opt = st.selectbox("Find by", ("Name and Last Name", "ID"))

    if 'client' not in st.session_state:
        st.session_state.client = {
            "name": "",
            "lastName": "",
            "address": "",
            "phones": [
                {
                    "areaCode": "",
                    "phoneNbr": "",
                    "phoneType": ""
                }
            ]
        }

    if opt == "ID":
        id = st.number_input("ID", 0)
        id_btn = st.button("Search")

        if id_btn:
            client = find_client_by_id(id)
            st.session_state.client = client  
    
    else:
        name = st.text_input("Name", "John")
        last_name = st.text_input("Last Name", "Doe")
        find_btn = st.button("Search")

        if find_btn:
            client = find_client_by_name_and_last_name(name, last_name)
            st.session_state.client = client 

    client = st.session_state.client

    st.subheader("Client Data")
    name = st.text_input("Name", client['name'], key="name_input")
    last_name = st.text_input("Last Name", client['lastName'], key="last_name_input")
    address = st.text_input("Address", client['address'], key="address_input")

    st.write("Phone Numbers")
    telephones = []

    for i, telephone in enumerate(client['phones']):
        with st.expander(f"Phone {i + 1}"):
            area_cod = st.text_input(f"Area Code {i + 1}", telephone['areaCode'], key=f"area_code_{i}")
            number = st.text_input(f"Number {i + 1}", telephone['phoneNbr'], key=f"number_{i}")

            phone_type = telephone['phoneType'] if telephone['phoneType'] in ("M", "F") else "M"
            phone_type = st.selectbox(f"Type {i + 1}", ("M", "F"), index=("M", "F").index(phone_type), key=f"phone_type_{i}")

            telephones.append({
                "areaCode": area_cod,
                "phoneNbr": number,
                "phoneType": phone_type
            })

    btn = st.button("Save")
    if btn:
        edit_client(client['clientNbr'], name, last_name, address, telephones)
        st.success("Client updated successfully.")
   
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
            delete_client(name['clientNbr'])
            st.success("Client deleted successfully.")



elif option == "Create Product":
    id = st.number_input("ID", 0)
    name = st.text_input("Name", "Product")
    brand = st.text_input("Brand", "Brand")
    description = st.text_area("Description", "Description")
    price = st.number_input("Price", 0.0)
    stock = st.number_input("Stock", 0)
    btn = st.button("Create")

    if btn:
        create_product(id, name, brand, description, price, stock)
        st.success("Product created successfully.")

elif option == "Modify Product":
    st.subheader("Find Product")
    opt = st.selectbox("Find by", ("ID",))

    if 'product' not in st.session_state:
        st.session_state.product = {
            "name": "",
            "brand": "",
            "price": 0.0,
            "description": "",
            "stock": 0,
            "codProduct": 0
        }

    if opt == "ID":
        id = st.number_input("ID", 0)
        find_btn = st.button("Search")

        if find_btn and id > 0:
            product = find_product_by_id(id)
            if product:
                st.session_state.product = product
                st.success("Product found.")
            else:
                st.session_state.product = {} 
                st.error("Product not found.")

    product = st.session_state.product

    if product and product.get('codProduct') > 0:  
        st.subheader("Product Data")

        name = st.text_input("Name", product['name'], key="name_input")
        brand = st.text_input("Brand", product['brand'], key="brand_input")
        price = st.number_input("Price", product['price'], key="price_input")
        description = st.text_area("Description", product['description'], key="description_input")
        stock = st.number_input("Stock", product['stock'], key="stock_input")

        btn = st.button("Edit")

        if btn:
            edit_product(product['codProduct'], name, brand, description, price, stock)
            st.success("Product updated successfully.")
    else:
        st.warning("Search for a product first.")
