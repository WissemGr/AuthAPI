# Use the official Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt /app/requirements.txt

# Install project dependencies
RUN pip install -r requirements.txt

# Copy the project files to the working directory
COPY . /app

# Expose the desired port (replace 5000 with the appropriate port number if needed)
EXPOSE 5000

# Set the entrypoint command (modify if needed)
CMD ["flask", "run", "--host=0.0.0.0"]
