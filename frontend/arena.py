import pandas as pd
import requests
import streamlit as st
import os

API_URL = os.getenv("ARENA_URL" , "http://localhost:8020")+"/arena/{execution_sheet}"


def show_arena_page():
    st.title("Lasso Execution Interface - Arena")

    # Arena Hauptinterface
    execution_sheet = st.text_input("Execution Sheet", value="calc7.xlsx")
    lql_string = st.text_area(
        "LQL String",
        value="""Matrix {\n      Matrix(list)->None\n        mean()->Any\n}""",
    )
    max_param_permutation_tries = st.number_input(
        "Max Param Permutation Tries", min_value=1, value=1
    )
    type_strictness = st.checkbox("Type Strictness", value=False)
    only_keep_top_n_mappings = st.number_input(
        "Only Keep Top N Mappings", min_value=1, value=10
    )
    allow_standard_value_constructor_adaptations = st.checkbox(
        "Allow Standard Value Constructor Adaptations", value=True
    )
    action_id = st.text_input("Action ID", value="PLACEHOLDER")
    record_metrics = st.checkbox("Record Metrics", value=True)

    if st.button("Execute"):
        url = API_URL.format(execution_sheet=execution_sheet)
        params = {
            "maxParamPermutationTries": max_param_permutation_tries,
            "typeStrictness": type_strictness,
            "onlyKeepTopNMappings": only_keep_top_n_mappings,
            "allowStandardValueConstructorAdaptations": allow_standard_value_constructor_adaptations,
            "actionId": action_id,
            "recordMetrics": record_metrics,
        }
        try:
            response = requests.post(url, params=params, data=lql_string)
            if response.status_code == 200:
                st.success("Execution completed successfully.")
                try:
                    data = response.json()
                    df = pd.DataFrame(data)
                    df['LASTMODIFIED'] = df['LASTMODIFIED'].astype(str)
                    st.dataframe(df)
                except ValueError:
                    st.text(response.text)
            else:
                st.error(f"Error: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
