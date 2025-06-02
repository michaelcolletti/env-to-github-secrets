# Stage 1: Build Stage
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
# --no-install-recommends prevents installation of recommended packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    # Clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker layer caching.
# If requirements.txt doesn't change, this layer won't be rebuilt.
COPY requirements.txt .
# Install Python dependencies. --no-cache-dir prevents pip from storing
# downloaded packages, further reducing image size.
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Stage
# Use a more specific and potentially smaller base image for the final stage.
# 'bookworm' is the current stable Debian release.
FROM python:3.13-slim-bookworm

# Create a non-root user for security.
# --system: creates a system user, suitable for services.
# --no-create-home: prevents creating a home directory, saving space.
# --group: creates a group with the same name.
RUN adduser --system --no-create-home --group env2sec

# Switch to the non-root user. This is a critical security practice.
USER env2sec

# Set the working directory for the application.
WORKDIR /app

# Copy only the necessary installed Python packages from the builder stage.
# This ensures build dependencies are not carried over to the final image.
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the rest of the application code.
# This should be done after dependencies to optimize caching.
COPY . .

# Set environment variables.
# PYTHONPATH: ensures Python can find your application modules.
ENV PYTHONPATH=/app
# PYTHONUNBUFFERED: ensures Python output is unbuffered, useful
#CMD ["python", "src/main.py"]

