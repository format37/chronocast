FROM python:3.9.18-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY app.py app.py

VOLUME /app/data

ENTRYPOINT ["python3", "app.py"]