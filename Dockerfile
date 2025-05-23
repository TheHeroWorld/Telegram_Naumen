FROM python:3.11
COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt --no-cache-dir


CMD ["python", "main.py"] 
