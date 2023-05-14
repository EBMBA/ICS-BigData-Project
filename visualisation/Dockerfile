FROM --platform=linux/amd64 python:3.9-slim-buster

WORKDIR /app

# Installation de Java
RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python et build-essential
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie des fichiers d'application
COPY . /app

# Configuration du JDBC SQLite
RUN mkdir -p /usr/local/lib/python3.9/site-packages/pyspark/jars/
RUN mv sqlite-jdbc.jar /usr/local/lib/python3.9/site-packages/pyspark/jars/

EXPOSE 3002

CMD ["python3", "main.py"]
