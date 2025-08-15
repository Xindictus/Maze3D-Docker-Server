###########################
# ----- basic pages ----- #
###########################
def test_home(client):
    resp = client.get("/")

    assert resp.status_code == 200
    assert b"This is an HTTP server for the Maze Experiment!" in resp.data


############################
# ----- /agent_ready ----- #
############################
def test_agent_ready_returns_player_ready(client, player_queue):
    player_queue.put({"command": "player_ready"})
    resp = client.get("/agent_ready")

    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json() == {"command": "player_ready"}


def test_agent_ready_timeout_bad_request(client):
    resp = client.get("/agent_ready")

    assert resp.status_code == 400
    assert b"Bad Request!" in resp.data


#######################
# ----- /config ----- #
#######################
def test_config_get_returns_current_config(client, server):
    resp = client.get("/config")

    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json() == server.config_data


def test_config_post_then_get(client):
    # POST
    new_cfg = {"alpha": 1, "agent_actions": [-1, 0, 1]}
    post_res = client.post("/config", json=new_cfg)

    assert post_res.status_code == 200
    assert post_res.get_json() == {"OK": "OK"}

    # GET
    get_res = client.get("/config")

    assert get_res.status_code == 200
    assert get_res.get_json() == new_cfg


##############################
# ----- /env_variables ----- #
##############################
def test_env_variables(client, server, monkeypatch):
    monkeypatch.setattr(
        server, "server_host", "http://localhost:8080", raising=True
    )
    resp = client.get("/env_variables")

    assert resp.status_code == 200
    assert resp.get_json() == {"host": "http://localhost:8080"}


#########################
# ----- /finished ----- #
#########################
def test_finished_enqueues_and_ok(client, agent_queue):
    resp = client.get("/finished")

    assert resp.status_code == 200
    assert resp.get_json() == {"OK": "OK"}

    msg = agent_queue.get_nowait()

    assert msg == {"command": "finished"}


############################
# ----- /observation ----- #
############################
def test_observation_posts_to_player_and_returns_agent_cmd(
    client, agent_queue
):
    agent_queue.put({"command": "1"})
    payload = {"obs": {"x": 1}}
    resp = client.post("/observation", json=payload)

    assert resp.status_code == 200
    assert resp.get_json() == {"command": "1"}


def test_observation_timeout_bad_request(client):
    resp = client.post("/observation", json={"obs": 1})

    assert resp.status_code == 400
    assert b"Bad Request!" in resp.data


#############################
# ----- /player_ready ----- #
#############################
def test_player_ready_enqueues_and_returns_agent_cmd(client, agent_queue):
    agent_queue.put({"command": "-1"})
    resp = client.get("/player_ready")

    assert resp.status_code == 200
    assert resp.get_json() == {"command": "-1"}


def test_player_ready_timeout_bad_request(client):
    resp = client.get("/player_ready")

    assert resp.status_code == 400
    assert b"Bad Request!" in resp.data


######################
# ----- /reset ----- #
######################
def test_reset_enqueues_and_waits_player_reset(
    client, player_queue, agent_queue
):
    # route will put {"command": "reset"} on agent,
    # then wait for player "reset"
    player_queue.put({"command": "reset"})
    resp = client.get("/reset")
    assert resp.status_code == 200
    assert resp.get_json() == {"command": "reset"}

    # verify agent got "reset"
    msg = agent_queue.get_nowait()
    assert msg == {"command": "reset"}


def test_reset_timeout_bad_request(client):
    resp = client.get("/reset")

    assert resp.status_code == 400
    assert b"Bad Request!" in resp.data


###########################
# ----- /reset_done ----- #
###########################
def test_reset_done_posts_to_player_and_returns_agent_cmd(client, agent_queue):
    agent_queue.put({"command": "0"})
    resp = client.post("/reset_done", json={"done": True})

    assert resp.status_code == 200
    assert resp.get_json() == {"command": "0"}


################################
# ----- /set_server_host ----- #
################################
def test_set_server_host_updates_global(client, server):
    resp = client.post("/set_server_host", json={"server_host": "127.0.0.1"})

    assert resp.status_code == 200
    assert resp.get_json() == {"OK": "OK"}
    assert server.server_host == "127.0.0.1"


#####################
# ----- /step ----- #
#####################
def test_step_enqueues_step_and_waits_player_step(
    client, agent_queue, player_queue
):
    # player must answer with a "step" command
    player_queue.put({"command": "step"})
    req = {"action": "1"}
    resp = client.post("/step", json=req)
    assert resp.status_code == 200
    assert resp.get_json() == {"command": "step"}

    # verify agent received the step request payload
    msg = agent_queue.get_nowait()
    assert msg["command"] == "step"
    assert msg["step_request"] == req


def test_step_timeout_bad_request(client):
    resp = client.post("/step", json={"action": "noop"})

    assert resp.status_code == 400
    assert b"Bad Request!" in resp.data


################################
# ----- /step_two_agents ----- #
################################
def test_step_two_agents_enqueues_and_waits_player_step(
    client, agent_queue, player_queue
):
    player_queue.put({"command": "step"})
    payload = {"foo": "1", "boo": "2"}
    resp = client.post("/step_two_agents", json=payload)

    assert resp.status_code == 200
    assert resp.get_json() == {"command": "step"}

    msg = agent_queue.get_nowait()

    assert msg["command"] == "step_two_agents"
    assert msg["step_request"] == payload


def test_step_two_agents_timeout_bad_request(client):
    resp = client.post("/step_two_agents", json={"foo": "1"})

    assert resp.status_code == 400
    assert b"Bad Request!" in resp.data


##########################
# ----- /testreset ----- #
##########################
def test_testreset_enqueues_testreset_and_waits_player_reset(
    client, agent_queue, player_queue
):
    player_queue.put({"command": "reset"})
    resp = client.get("/testreset")

    assert resp.status_code == 200
    assert resp.get_json() == {"command": "reset"}

    msg = agent_queue.get_nowait()

    assert msg == {"command": "testreset"}


#########################
# ----- /training ----- #
#########################
def test_training_enqueues_training_and_ok(client, agent_queue):
    payload = {"episodes": 10}
    resp = client.post("/training", json=payload)

    assert resp.status_code == 200
    assert resp.get_json() == {"OK": "OK"}

    msg = agent_queue.get_nowait()

    assert msg["command"] == "training"
    assert msg["training_request"] == payload
