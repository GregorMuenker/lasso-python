FROM python:3.12

# Set the working directory in the container to /app
WORKDIR /app

# Add the relevant directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "app.py"]
#CMD ["gunicorn","--config", "gunicorn_config.py", "app:app"]