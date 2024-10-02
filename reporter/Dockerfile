FROM python:3.9.16
WORKDIR /server
COPY requirements.txt /server
RUN pip install -r requirements.txt
COPY server.py /server
CMD ["python", "server.py"]