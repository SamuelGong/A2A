# A2A Use Toy Example

## 1. Prerequisite

```bash
pip install google-adk
```

## 2. Deploy

There is an Agent designed to sleep for the amount of time specified by a command line tool.
For communication, the agent is associated with an A2A server,
while the command line tool is associated with an A2A client.

To run them, in one terminal, first run the A2A server:

```bash
python a2a_server.py
# Example output during initialization:
# INFO:     Started server process [29879]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://localhost:20000 (Press CTRL+C to quit)
```

Then in another terminal, run the A2A client:

```bash
python a2a_client.py
# Example interaction:
# Discovered agent: Sleep Agent
# Enter seconds to sleep: 3
# The agent has slept for 1 seconds, leaving 2 seconds before waking up
# The agent has slept for 2 seconds, leaving 1 seconds before waking up
# The agent has slept for 3 seconds, leaving 0 seconds before waking up
# The agent asks: Extra seconds you want me to sleep: 2
# The agent has slept for 1 seconds, leaving 1 seconds before waking up
# The agent has slept for 2 seconds, leaving 0 seconds before waking up
# The agent asks: Extra seconds you want me to sleep: 0
# The agent finally says:  Thank you for using this agent!
```