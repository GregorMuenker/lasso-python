import streamlit as st
from arena import show_arena_page
from crawl import show_crawl_page

# Dictionary to hold the pages
pages = {"Home": "show_home_page", "Arena": show_arena_page, "Crawl": show_crawl_page}

# Sidebar for page navigation
st.sidebar.title("Navigation")
page_selection = st.sidebar.selectbox("Select a Page", list(pages.keys()))

# Display the selected page
if page_selection == "Home":
    st.title("Home Page")
    st.write("Welcome to the Home Page!")
    st.write("Use the sidebar to navigate between pages.")
else:
    pages[page_selection]()
