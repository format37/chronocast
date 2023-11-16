# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# COPY webhook_cert.pem /usr/src/app
# COPY webhook_pkey.pem /usr/src/app
# Copy SSL certificates
COPY cert/fullchain.pem /usr/src/app/
COPY cert/privkey.pem /usr/src/app/

COPY templates /usr/src/app/templates
COPY app.py /usr/src/app

# Make port 443 available to the world outside this container
EXPOSE 443

# Define environment variable
ENV NAME World

# Run app.py when the container launches
# CMD ["python", "app.py"]
# Run the Flask app with SSL
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:443", "--certfile", "webhook_cert.pem", "--keyfile", "webhook_pkey.pem", "app:app"]
CMD ["gunicorn", "-w", "4", "-b", "rtlm.info:443", "--certfile", "fullchain.pem", "--keyfile", "privkey.pem", "app:app"]
# gunicorn --certfile=fullchain.pem --keyfile=privkey.pem -b 0.0.0.0:443 your_flask_app:app
