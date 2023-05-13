FROM python:3.8

WORKDIR /app

# Installation de Java
RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Installation de gcc
RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copie des fichiers d'application
COPY . /app

# Installation des dépendances Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Configuration du JDBC SQLite
RUN mkdir -p /usr/local/lib/python3.8/site-packages/pyspark/jars/
RUN mv sqlite-jdbc.jar /usr/local/lib/python3.8/site-packages/pyspark/jars/

CMD ["python", "main.py"]
