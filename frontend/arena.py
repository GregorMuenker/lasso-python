import pandas as pd
import requests
import streamlit as st

API_URL = "http://localhost:8020/arena/{execution_sheet}"


def show_arena_page():
    st.title("Lasso Execution Interface - Arena")

    # Arena Hauptinterface
    execution_sheet = st.text_input("Execution Sheet", value="default_sheet")
    lql_string = st.text_area(
        "LQL String",
        value="""Calculator {\n    Calculator(int)->None\n    addme(int)->int\n    subme(int)->int\n}""",
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
                    st.dataframe(df)
                except ValueError:
                    st.text(response.text)
            else:
                st.error(f"Error: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
