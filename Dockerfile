# Use official Python slim image to keep the container lightweight
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency file first — Docker caches this layer separately so
# rebuilds are faster when only your code changes (not dependencies)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the app with uvicorn
# --host 0.0.0.0 makes it accessible outside the container
# --reload enables hot reloading when code changes (dev only)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
