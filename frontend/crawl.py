import requests
import streamlit as st

# Set up the API URL using the container name
API_URL = "http://lasso_python_crawl:8000/crawl/{package_name}"


def show_crawl_page():
    st.title("Crawl into SOLR Index")

    # Try to connect to the SOLR instance using the container name
    try:
        solr_url = "http://lasso_solr_quickstart:8983/solr/lasso_quickstart"
        ping_response = requests.get(solr_url + "/admin/ping")
        if ping_response.status_code == 200:
            st.sidebar.success("SOLR online")
            st.session_state.solr_online = True
        else:
            raise Exception("Ping failed")
    except Exception:
        st.sidebar.error("SOLR offline")
        st.session_state.solr_online = False

    # User input fields
    package_name = st.text_input("Package Name", key="package_name")
    type_inferencing_engine = st.selectbox("Type Inferencing Engine", (None, "HiTyper"))

    # Button to initiate crawling
    if st.button("Crawl Package", disabled=not st.session_state.solr_online):
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
