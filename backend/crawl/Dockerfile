FROM python:3.9

# Set the working directory in the container to /app
WORKDIR /app

# Add the relevant directory contents into the container at /app
ADD app.py /app
ADD requirements.txt /app
ADD crawl_pipeline.py /app
RUN sed -e '1,5d' -e  's/from backend.crawl //g' -e 's/from backend.crawl./from /g' /app/crawl_pipeline.py > /app/crawl_pipeline.py.bak
RUN mv /app/crawl_pipeline.py.bak /app/crawl_pipeline.py
ADD import_helper.py /app
ADD install.py /app
RUN sed -e '15,18d'  -e 's/from backend.crawl.nexus /from nexus /g' /app/install.py > /app/install.py.bak
RUN mv /app/install.py.bak /app/install.py
ADD nexus.py /app
RUN sed -e '10,13d' /app/nexus.py > /app/nexus.py.bak
RUN mv /app/nexus.py.bak /app/nexus.py
ADD splitting.py /app
RUN sed -e 's/from backend.crawl.nexus /from nexus /g' -e 's/from backend.crawl.install /from install /g' -e 's/from backend.crawl //g' /app/splitting.py > /app/splitting.py.bak
RUN mv /app/splitting.py.bak /app/splitting.py
ADD type_inference.py /app
RUN sed -e 's/from backend.crawl.inference_engines /from inference_engines /g' /app/type_inference.py > /app/type_inference.py.bak
RUN mv /app/type_inference.py.bak /app/type_inference.py
ADD inference_engines/hityper.py /app/inference_engines/hityper.py
ADD upload_index.py /app

# Update pip
RUN pip install --upgrade pip

# Install HDF5 using apt
RUN apt-get update && apt-get install -y libhdf5-dev

# Install h5py with no-binary flag
RUN pip install --no-binary h5py h5py

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable for runtime environment to "docker"
ENV RUNTIME_ENVIRONMENT="docker"

# Make port 80 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "app.py"]
#CMD ["gunicorn","--config", "gunicorn_config.py", "app:app"]