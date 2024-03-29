FROM python:3.12

WORKDIR /code

COPY requirements.txt .
COPY llm.py .
COPY server.py .

RUN pip install -r requirements.txt

