FROM python:3.12

WORKDIR /backend

COPY requirements.txt .
COPY llm.py .
COPY server.py .

RUN pip install -r requirements.txt

