FROM python:3.12-slim AS build

RUN apt-get update && \
    # -y: Automatically answers "yes" to prompts during the installation process
    apt-get upgrade -y && \
    # --no-install-recommends: install only the specified package and its essential dependencies, excluding any recommended (optional) packages
    apt-get install -y --no-install-recommends \
    # Required for uv installation
    curl && \
    # For Postgres if psycopg2 is used (not required for psycopg2-binary)
    # gcc \
    # libpq-dev && \
    # Removes cached files from /var/cache/apt/archives and /var/cache/apt/archives/partial that are used during the package installation process
    apt-get clean && \
    # Deletes the local copy of package metadata downloaded when you run apt-get update
    rm -rf /var/lib/apt/lists/*

ENV UV_INSTALLER=/uv-install.sh
# Download a pinned installer version (recommended)
# `$ pip index versions uv` to check available versions
ADD https://astral.sh/uv/0.7.1/install.sh $UV_INSTALLER
# OR: Download the latest installer version
# ADD https://astral.sh/uv/install.sh $UV_INSTALLER

# Run the installer then remove it
RUN chmod -R 755 $UV_INSTALLER && sh $UV_INSTALLER && rm $UV_INSTALLER

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Disable writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1

# Define stdout/stderr as unbuffered
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /opt/backend

# Copy dependencies if we work with pyproject.toml (.venv should be in .dockerignore)
COPY pyproject.toml uv.lock .python-version ./

# Sync dependencies
# RUN uv sync --locked

# Sync with extra dependencies (e.g. dev dependencies)
RUN uv sync --locked --all-extras

#########################################################

FROM python:3.12-slim AS final

RUN apt-get update && \
    # -y: Automatically answers "yes" to prompts during the installation process
    apt-get upgrade -y && \
    # --no-install-recommends: install only the specified package and its essential dependencies, excluding any recommended (optional) packages
    apt-get install -y --no-install-recommends \
    # For Postgres
    libpq5 && \
    # Removes cached files from /var/cache/apt/archives and /var/cache/apt/archives/partial that are used during the package installation process
    apt-get clean && \
    # Deletes the local copy of package metadata downloaded when you run apt-get update
    rm -rf /var/lib/apt/lists/*

# Set app path env variable
ENV APP=/opt/backend

# Set virtualenv path env variable
ENV VIRTUAL_ENV=$APP/.venv

# Make sure we use the virtualenv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set working directory
WORKDIR $APP

# Copy virtual environment folder from build stage
COPY --from=build $VIRTUAL_ENV $VIRTUAL_ENV

# Copy working dir contents
COPY . .

# Ensure run.sh is executable (if it is used)
RUN chmod +x ./run.sh

######## If uv is needed in the final image (optional, increases image size, use it in dev) ########
# COPY --from=build /root/.local /root/.local
# ENV PATH="/root/.local/bin/:$PATH"
####################################################################################################

# Keep container open for development
# CMD ["tail", "-f", "/dev/null"]
# OR: Start Django server (single command)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# OR: Run sh script for multiple commands
CMD ["./run.sh"]