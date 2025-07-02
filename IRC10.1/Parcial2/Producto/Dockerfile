FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-client \
        sshpass \
        ansible \
        iputils-ping \
        netbase \
        ca-certificates \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/logs

EXPOSE 5001

ENV ANSIBLE_HOST_KEY_CHECKING=False

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
