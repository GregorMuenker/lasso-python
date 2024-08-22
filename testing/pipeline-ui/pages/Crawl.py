import json

import pysolr
import streamlit as st
import sys
import os

project_path = os.path.abspath(os.path.join('../..'))

# check the path is not already in sys.path, to avoid duplicates
if project_path not in sys.path:
    sys.path.insert(0, project_path)

import backend.crawl.crawl_pipeline

try:
    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr = pysolr.Solr(solr_url, always_commit=True)
    ping = solr.ping()
    st.sidebar.success("SOLR online")
    st.session_state.solr_online = True
except Exception:
    st.sidebar.error("SOLR offline")
    st.session_state.solr_online = False

st.markdown("# Crawl into SOLR Index")

st.text_input("Package Name", key="package_name")
#st.text_input("Package Version", key="package_version")
st.selectbox("Type Inferencing Engine", (None, "HiTyper"))
if st.button("Crawl Package", disabled=not st.session_state.solr_online):#
    with st.spinner(f"Crawling {st.session_state.package_name}"):
        backend.crawl.crawl_pipeline.index_package(st.session_state.package_name)