FROM python:3.9.16
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir
COPY app.py /app
CMD ["python3", "app.py"]