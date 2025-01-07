FROM python:3.12

RUN mkdir /app && apt-get update && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
COPY . /app
EXPOSE 5050

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
