# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# COPY server/webhook_cert.pem /usr/src/app
# COPY server/webhook_pkey.pem /usr/src/app
COPY index.html /usr/src/app
COPY app.py /usr/src/app

# Expose port 80 for HTTP traffic
EXPOSE 80

# Expose port 443 for HTTPS traffic
EXPOSE 443

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "./app.py"]
