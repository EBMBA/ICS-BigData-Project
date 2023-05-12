# Python Alpine n'a pas les dépendances pour Panda
FROM python:3.8

WORKDIR /app

COPY . /app
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
