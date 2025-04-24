import sys
import logging
import traceback

import click
from sleeping_agent import SleepingAgent
from task_manager import AgentTaskManager

sys.path.append('../..')  # change it when necessary
from common.server.server import A2AServer
from common.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="localhost", help="Server host")
@click.option("--port", default=20000, help="Server port", type=int)
def main(host, port):
    try:
        # Define Agent Card & Capabilities
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="sleep_skill",
            name="Sleep Skill",
            description="Simulate sleeping for a given number of seconds.",
            tags=["sleep", "demo"],
            examples=["Sleep for 5 seconds."]
        )
        agent_card = AgentCard(
            name="Sleep Agent",
            description="This agent handles the sleep request given the amount of time to sleep for.",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=SleepingAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=SleepingAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=SleepingAgent()),
            host=host,
            port=port,
        )
        server.start()
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}\n{traceback.format_exc()}")
        exit(1)


if __name__ == "__main__":
    main()
