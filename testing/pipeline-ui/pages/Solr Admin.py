import time

import pysolr
import requests
import streamlit as st

st.markdown("# SOLR Admin Panel")

try:
    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr = pysolr.Solr(solr_url, always_commit=True)
    ping = solr.ping()
    st.sidebar.success("SOLR online")
    st.session_state.solr_online = True
except Exception:
    st.sidebar.error("SOLR offline")
    st.session_state.solr_online = False

if st.button("Clear SOLR", disabled=not st.session_state.solr_online):
    res = requests.post('http://localhost:8983/solr/lasso_quickstart/update?commit=true',
                        json={"delete": {"query": "*:*"}})
    if res.json()["responseHeader"]["status"] == 0:
        msg = st.sidebar.success("SOLR cleared")
        time.sleep(3)
        msg.empty()

