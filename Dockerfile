# Use a slim Python base image
FROM python:3.9-slim

# 1) Set a working directory
WORKDIR /app

# 2) Copy only requirements.txt (for layer caching)
COPY requirements.txt .

# 3) Install system-level dependencies (if needed for any packages)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4) Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copy the rest of your project into /app
COPY . .

# 6) (Optional) If you want to bake in a .env file, uncomment:
# COPY .env .env

# 7) By default, run main.py when the container starts
CMD ["python", "main.py"]
