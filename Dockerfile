FROM python:3.12-slim

# Install Chromium and ChromeDriver for ARM compatibility
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure data and output directories exist
RUN mkdir -p /app/data /app/output

# Expose port for web interface
EXPOSE 8000

# Run the web server
CMD ["python", "src/api.py"]
