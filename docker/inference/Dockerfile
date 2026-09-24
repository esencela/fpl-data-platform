FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary scripts
COPY src/inference/ ./src/inference/
COPY src/config/ ./src/config/

ENV PYTHONPATH=/app/src

ENTRYPOINT ["python", "src/inference/main.py"]