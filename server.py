import logging
from queue import Queue

import werkzeug
from environs import Env
from flask import Flask, request
from flask_cors import CORS

# App init
app = Flask(__name__)
CORS(app)

# Reuse GUNICORN logger
gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
# keep logs from duplicating
app.logger.propagate = False

env = Env()
agent = Queue(maxsize=1)
player = Queue(maxsize=1)

config_data = None
timeout = env("TIMEOUT", 10)
server_host = env("HOST", "https://maze-server.app.orbitsystems.gr")


def message_by(queue: Queue, data: dict):
    if queue.full():
        queue.get()
    queue.put(data)


def assert_player_command(res, command):
    if "command" in res and res["command"] == command:
        return res

    try:
        return player.get(timeout=timeout)
    except Exception as e:
        app.logger.warning(f"Unable to get player command: {e}")


@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return "Bad Request!", 400


@app.route("/")
def home():
    return "This is an HTTP server for the Maze Experiment!"


@app.route("/agent_ready")
def agent_ready():
    """Initiated by agent"""
    app.logger.info("agent->ready")

    try:
        cmd = player.get(timeout=timeout)
        return assert_player_command(cmd, "player_ready")
    except Exception as e:
        return handle_bad_request(e)


@app.route("/config", methods=["GET", "POST"])
def config():
    global config_data
    if request.method == "GET":
        app.logger.info(config_data)
        return config_data
    if request.method == "POST":
        config_data = request.json
        return {"OK": "OK"}


@app.route("/env_variables")
def env_variables():
    return {"host": server_host}


@app.route("/finished")
def finished():
    """Initiated by agent"""
    app.logger.info("agent->finished")
    message_by(agent, {"command": "finished"})
    return {"OK": "OK"}


@app.route("/observation", methods=["POST"])
def observation():
    """Initiated by player"""
    app.logger.info("player->observation")
    message_by(player, request.json)

    try:
        cmd = agent.get(timeout=timeout)
        return cmd
    except Exception as e:
        return handle_bad_request(e)


@app.route("/player_ready")
def player_ready():
    """Initiated by player"""
    app.logger.info("player->player_ready")
    message_by(player, {"command": "player_ready"})

    try:
        cmd = agent.get(timeout=timeout)
        return cmd
    except Exception as e:
        return handle_bad_request(e)


@app.route("/reset")
def reset():
    """Initiated by agent"""
    app.logger.info("agent->reset")
    message_by(agent, {"command": "reset"})

    try:
        cmd = player.get(timeout=timeout)
        return assert_player_command(cmd, "reset")
    except Exception as e:
        return handle_bad_request(e)


@app.route("/reset_done", methods=["POST"])
def reset_done():
    """Initiated by player"""
    app.logger.info("player->reset_done")
    message_by(player, request.json)

    try:
        cmd = agent.get(timeout=timeout)
        return cmd
    except Exception as e:
        return handle_bad_request(e)


@app.route("/set_server_host", methods=["POST"])
def set_server_host():
    global server_host
    server_host = request.json["server_host"]
    return {"OK": "OK"}


@app.route("/step", methods=["POST"])
def step():
    """Initiated by agent"""
    message_by(agent, {"command": "step", "step_request": request.json})

    try:
        cmd = player.get(timeout=timeout)
        return assert_player_command(cmd, "step")
    except Exception as e:
        return handle_bad_request(e)


@app.route("/step_two_agents", methods=["POST"])
def step_two_agents():
    """Initiated by agent"""
    message_by(
        agent, {"command": "step_two_agents", "step_request": request.json}
    )

    try:
        cmd = player.get(timeout=timeout)
        return assert_player_command(cmd, "step")
    except Exception as e:
        return handle_bad_request(e)


@app.route("/testreset")
def testreset():
    """Initiated by agent"""
    app.logger.info("agent->testreset")
    message_by(agent, {"command": "testreset"})

    try:
        cmd = player.get(timeout=timeout)
        return assert_player_command(cmd, "reset")
    except Exception as e:
        return handle_bad_request(e)


@app.route("/training", methods=["POST"])
def training():
    """Initiated by agent"""
    app.logger.info("agent->training", request.json)
    message_by(
        agent, {"command": "training", "training_request": request.json}
    )
    return {"OK": "OK"}


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
