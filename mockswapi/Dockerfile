FROM python:3.12-slim

RUN apt-get update && \
    # Removes cached files from /var/cache/apt/archives and /var/cache/apt/archives/partial that are used during the package installation process
    apt-get clean && \
    # Deletes the local copy of package metadata downloaded when you run apt-get update
    rm -rf /var/lib/apt/lists/*

# Disable writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1

# Define stdout/stderr as unbuffered
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/mockswapi

RUN pip install fastapi uvicorn

COPY main.py /opt/mockswapi

# Keep container open for development
# CMD ["tail", "-f", "/dev/null"]
# OR: Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]