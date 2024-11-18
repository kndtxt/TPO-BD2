import streamlit as st
from lib.bills_data import get_name_and_last_name_amount_of_bills, get_bills_by_name_and_last_name, get_bills_with_products_from_brand, get_name_last_name_money_spent, get_bill_data_ordered_by_dates, get_products_not_billed, get_products_billed_at_least_once

st.title("Bills")

option = st.selectbox(
    "Test the functionality of the Project",
    (
        "Name and Last Name <> Amount of Bills",
        "Bills by Name and Last Name",
        "Bills with products from a particular brand",
        "Name and Last Name <> what was spent",
        "Bill data ordered by dates",
        "Products that were not billed",
        "Products billed at least once"
    ),
)

if option == "Name and Last Name <> Amount of Bills":
    data = get_name_and_last_name_amount_of_bills()
    for client in data:
        st.write(f"**{client}**: {data[client]} bills")
 

# TODO: check
elif option == "Bills by Name and Last Name":
    name = st.text_input("Name", "Kai")
    last_name = st.text_input("Last Name", "Bullock")
    btn = st.button("Search")

    if btn:
        data = get_bills_by_name_and_last_name(name, last_name)
        st.write(data)

# TODO: check
elif option == "Bills with products from a particular brand":
    brand = st.text_input("Brand", "Ipsum")
    btn = st.button("Search")

    if btn:
        data = get_bills_with_products_from_brand(brand)
        if data == []:
            st.write("No bills found")
        else:
            st.write(data)

elif option == "Name and Last Name <> what was spent":
    data = get_name_last_name_money_spent()
    for client in data:
        st.write(f"**{client}**: ${data[client]:.2f}")

elif option == "Bill data ordered by dates":
    data = get_bill_data_ordered_by_dates()
    for bill in data:
        st.write(f"**Bill Number**: {bill['billNbr']}")
        st.write(f"**Date**: {bill['date']}")
        st.write(f"**Total**: ${bill['total']:.2f}")
        st.write(f"**Tax**: {bill['tax']}%")
        st.write(f"**Taxed Total**: ${bill['taxxedTotal']:.2f}")
        st.write(f"**Client Number**: {bill['clientNbr']}")
        st.write("**Details**")
        for detail in bill['details']:
            st.write(f"**Product Code**: {detail['codProduct']} **Item Number**: {detail['itemNbr']} **Amount**: {detail['amount']}")
        st.write("--------------------")
        st.write("")

elif option == "Products that were not billed":
    data = get_products_not_billed()['data']
    for product in data:
        st.write(f"**Product Code**: {product['codProduct']} **Brand**: {product['brand']} **Description**: {product['description']}")

elif option == "Products billed at least once":
    data = get_products_billed_at_least_once()
    for product in data:
        st.write(f"**Product Code**: {product['codProduct']} **Brand**: {product['brand']} **Description**: {product['description']}")



