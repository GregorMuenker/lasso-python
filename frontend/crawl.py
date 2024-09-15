import requests
import streamlit as st
import os

# Set up the API URL using the container name
API_URL = os.getenv("CRAWL_URL" , "http://localhost:8010")+"/crawl/{package_name}"


def show_crawl_page():
    st.title("Crawl into SOLR Index")

    # User input fields
    package_name = st.text_input("Package Name", key="package_name")
    type_inferencing_engine = st.selectbox("Type Inferencing Engine", (None, "HiTyper"))

    # Button to initiate crawling
    if st.button("Crawl Package"):
        with st.spinner(f"Crawling {package_name}..."):
            params = {"type_inferencing_engine": type_inferencing_engine}
            url = API_URL.format(package_name=package_name)
            try:
                response = requests.post(url, params=params)
                if response.status_code == 200:
                    st.success(f"Successfully crawled package {package_name}.")
                else:
                    st.error(
                        f"Failed to crawl package. Status code: {response.status_code}"
                    )
                    st.text(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
