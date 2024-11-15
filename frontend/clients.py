import streamlit as st

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
    # TODO: Endpoint that returns all clients data 
    st.write("Client Data")

elif option == "Show telephone numbers by Name and Last Name":
    name = st.text_input("Name", "Jaboc")
    last_name = st.text_input("Last Name", "Cooper")
    btn = st.button("Search")
    # TODO: Endpoint that returns telephone numbers by Name and Last Name
    st.write("telephone numbers by Name and Last Name")

elif option == "Show telephone <> client data":
    # TODO: Endpoint that returns telephone <> client data
    st.write("telephone <> client data")

elif option == "Show clients with at least one bill":
    # TODO: Endpoint that returns clients with at least one bill
    st.write("clients with at least one bill")

elif option == "Show clients without bills":
    # TODO: Endpoint that returns clients without bills
    st.write("clients without bills")

elif option == "Clients <> Number of bills":
    # TODO: Endpoint that returns clients <> number of bills
    st.write("Clients <> Number of bills")
