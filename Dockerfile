# Sales Bike Agent - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for FAISS indices
RUN mkdir -p data/indices

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5.0)"

# Run setup script if indices don't exist, then start server
CMD if [ ! -f "data/indices/products.index" ]; then \
        echo "Building FAISS indices..." && \
        python -m src.data.setup_vector_store; \
    fi && \
    echo "Starting Sales Bike Agent API..." && \
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000
