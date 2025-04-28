# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copier et exécuter le script d'installation des drivers SQL Server
COPY install_sql_driver.sh install_sql_driver.sh
RUN chmod +x ./install_sql_driver.sh && ./install_sql_driver.sh

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN echo "Installing Python dependencies..." && \
    pip install --no-cache-dir -r requirements.txt gunicorn pyodbc

RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

# Copy the application code into the container
COPY . .

# Expose the port the application will run on
EXPOSE 8001

# Define environment variables inside the container
ENV ENV_FILE_PATH=/app/.env

# Run the application using Gunicorn with Uvicorn workers for FastAPI
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8001", "app.main:app"]
