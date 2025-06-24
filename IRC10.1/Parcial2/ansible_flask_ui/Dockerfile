FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y ansible openssh-client && \
    pip install flask

COPY . .

RUN chmod 600 /app/keys/id_rsa

CMD ["python", "app/app.py"]
