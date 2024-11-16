import streamlit as st

pg = st.navigation([
	st.Page("clients.py", title="Clients"),
	st.Page("bills.py", title="Bills"),
	st.Page("crud.py", title="CRUD")
])

pg.run()
