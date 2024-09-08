import pysolr
import streamlit as st

try:
    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr = pysolr.Solr(solr_url, always_commit=True)
    ping = solr.ping()
    st.sidebar.success("SOLR online")
    st.session_state.solr_online = True
except Exception:
    st.sidebar.error("SOLR offline")
    st.session_state.solr_online = False

st.markdown("# Search SOLR")
st.text_input("Function Name", key="name")
if st.button("Search"):
    res = solr.search(f"method:{st.session_state.name}", rows=3000)
    for doc in res.docs:
        container = st.container(border=True)
        col1, col2 = container.columns(2)
        col1.write("*Name*")
        col1.write(f"**{doc['method'][0]}**")
        col2.write("*Module*")
        col2.write(f"**{doc['packagename'][0]}**")
        with container.expander("Full Details"):
            st.write(doc)