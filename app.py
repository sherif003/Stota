import streamlit as st
from products import products_page
from orders import orders_page
from reports import reports_page
from refund_page import refund_page

st.sidebar.title("Stota Store POS System")
page = st.sidebar.radio("Select Page", [ "Orders","Products", "Reports & Cash Breakdown","Refund Page"])

if page == "Products":
    products_page()
elif page == "Orders":
    orders_page()
elif page == "Reports & Cash Breakdown":
    reports_page()
elif page == "Refund Page":
    refund_page()
