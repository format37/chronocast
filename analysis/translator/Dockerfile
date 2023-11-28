FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel
# FROM huggingface/transformers-gpu:4.18.0

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY app.py app.py

VOLUME /app/cache

ENTRYPOINT ["python3", "app.py"]