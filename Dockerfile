# Etapa 1: build
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Etapa 2: runtime
FROM python:3.9-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY src/ .

EXPOSE 8080
ENV APP_VERSION=2.0.0

ENV APP_PORT=8080
ENV APP_DEBUG=true

CMD ["python", "app.py"]

