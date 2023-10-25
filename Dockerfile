# Use the official Python 3.11.1 image as the base image
FROM python:3.11.1-slim

# Set the working directory within the container to /app
WORKDIR /app

# Set environment variables to improve Python behavior within the container
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the requirements.txt file from the host to the container
COPY requirements.txt .

# Update the package list and install system dependencies
RUN apt-get update \
    && apt-get -y install libpq-dev gcc

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the entire project directory from the host to the container's /app directory
COPY . .
