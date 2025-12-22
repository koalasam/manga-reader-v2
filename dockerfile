FROM python:3.11-slim

# Repository to clone (can be overridden at build time with --build-arg REPO_URL=...)
ARG REPO_URL=https://github.com/koalasam/manga-reader-v2.git

# Set working directory
WORKDIR /app

# Install system dependencies (git for cloning, libs for Pillow)
RUN apt-get update && apt-get install -y \
    git \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo and copy files into the image
RUN git clone --depth 1 "$REPO_URL" /tmp/app_src \
    && rm -rf /tmp/app_src/.git \
    && cp -a /tmp/app_src/. /app/ \
    && rm -rf /tmp/app_src

# Install Python dependencies from the cloned repo
RUN pip install --no-cache-dir -r /app/requirements.txt

# Ensure data directory exists
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]