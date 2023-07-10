# Use the official Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the project files to the working directory
COPY . /app

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the desired port (replace 5000 with the appropriate port number if needed)
EXPOSE 5000

# Set the entrypoint command (modify if needed)
CMD ["python", "app/__init__.py"]
