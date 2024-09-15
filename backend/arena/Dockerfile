FROM python:3.12

# Set the working directory in the container to /app
WORKDIR /app

# Add the relevant directory contents into the container at /app
ADD constants.py /app
RUN sed -e '6,14d' /app/constants.py > /app/constants.py.bak
RUN mv /app/constants.py.bak /app/constants.py
ADD app.py /app
ADD test_data_file.py /app
ADD requirements.txt /app
ADD import_helper.py /app
ADD nexus.py /app
RUN sed -e '10,13d' /app/nexus.py > /app/nexus.py.bak
RUN mv /app/nexus.py.bak /app/nexus.py
ADD lasso_solr_connector.py /app
RUN sed  -e 's/from backend.arena./from /g' /app/lasso_solr_connector.py > /app/lasso_solr_connector.py.bak
RUN mv /app/lasso_solr_connector.py.bak /app/lasso_solr_connector.py
ADD sequence_specification.py /app
ADD ignite.py /app
ADD adaptation_identification.py /app
RUN sed -e '8,12d' -e 's/from backend.constants /from constants /g' /app/adaptation_identification.py > /app/adaptation_identification.py.bak
RUN mv /app/adaptation_identification.py.bak /app/adaptation_identification.py
ADD adaptation_implementation.py /app
RUN sed -e '12,16d' -e 's/from backend.arena./from /g' -e 's/from backend.constants /from constants /g' /app/adaptation_implementation.py > /app/adaptation_implementation.py.bak
RUN mv /app/adaptation_implementation.py.bak /app/adaptation_implementation.py
ADD execution.py /app
RUN sed -e '11,15d' -e 's/from backend.constants /from constants /g' -e 's/from backend.arena./from /g' /app/execution.py > /app/execution.py.bak
RUN mv /app/execution.py.bak /app/execution.py
ADD lql/ /app/lql
RUN sed -e '10,12d' -e 's/from backend.arena./from /g' -e 's/repo.working_tree_dir)#//g'  -e 's/backend.constants /constants /g' /app/lql/antlr_parser.py > /app/lql/antlr_parser.py.bak
RUN mv /app/lql/antlr_parser.py.bak /app/lql/antlr_parser.py

ADD execution_sheets/ /app/execution_sheets

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable for runtime environment to "docker"
ENV RUNTIME_ENVIRONMENT="docker"

# Make port 80 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "app.py"]
#CMD ["gunicorn","--config", "gunicorn_config.py", "app:app"]