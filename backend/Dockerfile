FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start the application
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "api:app", "--bind", "0.0.0.0:8000", "--timeout", "600"]
