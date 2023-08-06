# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install uvicorn
RUN pip install uvicorn

# Expose the port that your FastAPI application is running on (if applicable)
EXPOSE 8000

# Command to run your FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
