# Use Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements (if you have requirements.txt)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Run Flask
CMD ["sh", "entrypoint.sh"]
