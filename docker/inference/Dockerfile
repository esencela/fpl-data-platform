FROM python:3.11-slim

# LightGBM's core uses OpenMP for multi-threading
# Requires libgomp, a system-level shared library
# Not included in slim python image
# Install seperately to pip install
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY docker/inference/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary scripts
COPY src/inference/ ./src/inference/
COPY src/config/ ./src/config/

ENV PYTHONPATH=/app/src

ENTRYPOINT ["python", "src/inference/main.py"]