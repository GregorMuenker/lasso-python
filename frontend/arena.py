import time

import docker
import pandas as pd
import requests
import streamlit as st

API_URL = "http://localhost:8020/arena/{execution_sheet}"


# Function to check if required containers are running
def check_containers():
    try:
        client = docker.from_env()
        required_containers = [
            "lasso_ignite",
            "lasso_python_crawl",
            "lasso_python_arena",
            "lasso_solr_quickstart",
            "lasso-nexus",
        ]
        running_containers = client.containers.list()
        running_names = [container.name for container in running_containers]
        missing_containers = [
            name for name in required_containers if name not in running_names
        ]
        if missing_containers:
            return False, missing_containers
        else:
            return True, []
    except Exception as e:
        st.error(f"An error occurred while checking containers: {e}")
        return False, []


# Retry logic with a timer
max_retries = 8
retry_delay = 15  # seconds


def retry_check():
    for attempt in range(1, max_retries + 8):
        st.write(
            f"Attempt {attempt}/{max_retries}: Checking if all containers are running..."
        )
        containers_running, missing_containers = check_containers()
        if containers_running:
            st.success("All required containers are running.")
            return True
        st.warning(
            f"The following containers are not running: {', '.join(missing_containers)}"
        )
        if attempt < max_retries:
            for remaining_time in range(retry_delay, 0, -1):
                st.write(f"Retrying in {remaining_time} seconds...")
                time.sleep(1)
    st.error("Not all containers are running after multiple attempts.")
    st.warning("Please restart the application or reload this page.")
    return False


def show_arena_page():
    st.title("Lasso Execution Interface - Arena")

    containers_running = retry_check()

    if containers_running:
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
    else:
        st.stop()
