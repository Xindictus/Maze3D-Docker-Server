# Maze Experiment HTTP Server

## Build and run locally

1. Install `uv` dependency manager. Follow installation instructions [here](https://docs.astral.sh/uv/getting-started/installation/).
2. Install `Python` dependencies:

   ```shell
   uv sync
   ```

3. Enable `venv`:

   ```shell
   . .venv/bin/activate
   ```

4. Install `pre-commit` hooks to enforce code formatting when committing:

   ```shell
   uv run pre-commit install
   ```

5. Run `gunicorn` server:

   ```shell
   python server.py
   ```

## Build and run via Docker

```shell
# build the docker image with some tag ex. maze-http-server
docker build -t maze-http-server:1.0.0 .

# run the docker image with -d for detached
# and -p "<host PORT>:<container PORT>" for port mappings
docker run -d -p 8080:5050 -e HOST="http://localhost:8080" maze-http-server:1.0.0
```
