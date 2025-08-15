FROM python:3.13-slim

ENV WDIR=/maze-3d-docker

# Install uv dependency manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /maze-3d-docker

# Copy repo code
COPY ./ ./

# Install LIVE dependencies only
RUN uv sync --no-dev

EXPOSE 5050

# Enable GUNICORN access logs
ENV GUNICORN_CMD_ARGS="--access-logfile - --error-logfile - --log-level info"

CMD ["uv", "run", "gunicorn", "server:app"]
