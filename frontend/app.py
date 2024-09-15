import time

import docker
import requests
import streamlit as st

# Set the URL of your FastAPI endpoint
API_URL = "http://localhost:8020/arena/{execution_sheet}"

st.title("Lasso Execution Interface")


# Function to check if required containers are running
def check_containers():
    try:
        client = docker.from_env()
        # List of required container names based on your docker-compose.yml
        required_containers = [
            "lasso_ignite",
            "lasso_python_crawl",
            "lasso_python_arena",
            "lasso_solr_quickstart",
            "lasso-nexus",
            "lasso_frontend",
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
    for attempt in range(1, max_retries + 1):
        st.write(
            f"Attempt {attempt}/{max_retries}: Checking if all containers are running..."
        )
        containers_running, missing_containers = check_containers()

        if containers_running:
            st.success("All required containers are running.")
            return True

        # If containers are missing, display which ones
        st.warning(
            f"The following containers are not running: {', '.join(missing_containers)}"
        )

        # Display countdown timer
        if attempt < max_retries:
            for remaining_time in range(retry_delay, 0, -1):
                st.write(f"Retrying in {remaining_time} seconds...")
                time.sleep(1)

    # After all attempts fail
    st.error("Not all containers are running after multiple attempts.")
    st.warning("Please restart the application or reload this page.")
    return False


# Check if containers are running with retries
containers_running = retry_check()

if containers_running:
    # Input fields for Execution Sheet and LQL String
    execution_sheet = st.text_input("Execution Sheet", value="default_sheet")
    lql_string = st.text_area(
        "LQL String",
        value="""
    Calculator {
        Calculator(int)->None
        addme(int)->int
        subme(int)->int
    }
    """,
    )

    # When the user clicks "Execute"
    if st.button("Execute"):
        # Format the URL with the provided execution_sheet
        url = API_URL.format(execution_sheet=execution_sheet)

        # Send the POST request to the endpoint
        try:
            response = requests.post(url, data=lql_string)
            if response.status_code == 200:
                st.success("Execution completed successfully.")

                # Try to parse the response as JSON
                try:
                    output = response.json()
                    st.json(output)
                except ValueError:
                    # If response is not JSON, display as text
                    st.text(response.text)
            else:
                st.error(f"Error: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.stop()  # Stop the script if containers are not running
