import streamlit as st

st.title("Bills")

option = st.selectbox(
    "Test the functionality of the Project",
    (
        "Bills by Name and Last Name",
        "Bills with products from a particular brand",
        "Name and Last Name <> what was spent",
        "Bill data ordered by dates",
        "Products that were not billed",
        "Products billed at least once"
    ),
)

if option == "Bills by Name and Last Name":
    name = st.text_input("Name", "Kai")
    last_name = st.text_input("Last Name", "Bullock")
    btn = st.button("Search")
    # TODO: Endpoint that returns bills by Name and Last Name

elif option == "Bills with products from a particular brand":
    brand = st.text_input("Brand", "Ipsum")
    btn = st.button("Search")
    # TODO: Endpoint that returns bills with products from a particular brand

elif option == "Name and Last Name <> what was spent":
    # TODO: Endpoint that returns Name and Last Name <> what was spent
    st.write("Name and Last Name <> what was spent")

elif option == "Bill data ordered by dates":
    # TODO: Endpoint that returns bill data ordered by dates
    st.write("Bill data ordered by dates")

elif option == "Products that were not billed":
    # TODO: Endpoint that returns products that were not billed
    st.write("Products that were not billed")

elif option == "Products billed at least once":
    # TODO: Endpoint that returns products billed at least once
    st.write("Products billed at least once")



