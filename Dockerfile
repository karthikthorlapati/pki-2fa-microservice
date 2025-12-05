# Dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
ENV TZ=UTC

# Install Cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copy Dependencies and Code
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# Configure Cron
COPY jobs/periodic_task /etc/cron.d/vault-task
RUN chmod 0644 /etc/cron.d/vault-task && crontab /etc/cron.d/vault-task

# CRITICAL FIX: Create the directories required by the assignment
RUN mkdir -p /data /cron

# Start Services
CMD cron && uvicorn core.api_gateway:gateway --host 0.0.0.0 --port 8080