import queue

import pytest


@pytest.fixture
def server(monkeypatch):
    # Import server module
    import server as _server

    # Small queues for each test
    agent_q = queue.Queue(maxsize=8)
    player_q = queue.Queue(maxsize=8)

    monkeypatch.setattr(_server, "agent", agent_q, raising=True)
    monkeypatch.setattr(_server, "player", player_q, raising=True)

    # Override for faster timeouts
    monkeypatch.setattr(_server, "timeout", 0.01, raising=True)

    # Default config/server_host
    monkeypatch.setattr(
        _server, "config_data", {"default": True}, raising=False
    )
    monkeypatch.setattr(_server, "server_host", "127.0.0.1", raising=False)

    return _server


@pytest.fixture
def app(server):
    server.app.config.update(TESTING=True)
    return server.app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def agent_queue(server):
    return server.agent


@pytest.fixture
def player_queue(server):
    return server.player
