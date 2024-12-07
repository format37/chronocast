FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel

WORKDIR /app

# Install Google Cloud SDK
RUN apt-get update && apt-get install -y curl
RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/root/google-cloud-sdk/bin

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY bucket.py bucket.py
COPY app.py app.py

# Create directory for Google Cloud credentials
RUN mkdir -p /root/.config/gcloud

VOLUME /app/cache

# Add volume for Google Cloud credentials
VOLUME /root/.config/gcloud

ENTRYPOINT ["python3", "app.py"]