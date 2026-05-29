FROM python:3.11-slim

WORKDIR /app

# Install dbt
RUN pip install --no-cache-dir dbt-postgres

# Copy the dbt project files into the container
COPY dbt/ ./dbt/

# Install dbt dependencies
WORKDIR /app/dbt
RUN dbt deps

CMD ["dbt", "--version"]