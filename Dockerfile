

# Build Stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final Stage
FROM python:3.11-slim
WORKDIR /app
ENV TZ=UTC

# System Dependencies
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copy Python Artifacts
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# Configure Periodic Job (Cron)
# Copying from new location 'jobs/periodic_task'
COPY jobs/periodic_task /etc/cron.d/vault-task
RUN chmod 0644 /etc/cron.d/vault-task && crontab /etc/cron.d/vault-task

# Create Volume Directories
# /vault_data stores the decrypted seed
# /vault_logs stores the audit runner output
RUN mkdir -p /vault_data /vault_logs

# Launch Service
# "core.api_gateway:gateway" refers to core/api_gateway.py and the "gateway = FastAPI()" object
CMD cron && uvicorn core.api_gateway:gateway --host 0.0.0.0 --port 8080