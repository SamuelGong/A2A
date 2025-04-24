import sys
import json
import asyncio
import logging
from typing import AsyncIterable
from typing_extensions import override

from google.adk.runners import Runner
from google.adk.agents import BaseAgent
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.events.event import Event
from google.genai import types as genai_types

sys.path.append('../..')  # change it when necessary
from common.types import (
    TaskStatus,
    TaskState,
    Message,
    TextPart,
    TaskStatusUpdateEvent
)


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InternalSleepingAgent(BaseAgent):
    """
    SleepingAgent:
      1) WORKING: sleep initial seconds (streaming progress).
      2) INPUT_REQUIRED: prompt for extra seconds.
      3) WORKING: sleep extra seconds (if >0).
      4) COMPLETED: emit total slept time as artifact.
    """

    @override
    async def _run_async_impl(self, ctx):
        # 1) Parse initial duration
        # print(ctx.__dict__)
        init_secs = int(ctx.user_content.parts[0].text)
        total = init_secs
        print(f'[Debug] Initial time to sleep in sec: {total}')

        # 2) WORKING: initial sleep loop
        if init_secs > 0:
            for elapsed in range(1, init_secs + 1):
                await asyncio.sleep(1)

                yield Event(
                    invocation_id=ctx.invocation_id,
                    author=self.name,
                    branch=ctx.branch,
                    content=genai_types.Content(
                        role='agent',
                        parts=[TextPart(text=json.dumps({
                            "elapsed": elapsed,
                            "remaining": init_secs - elapsed
                        }))]
                    ),
                    partial=True  # such that event.is_final_response is not true726877
                )

            # 3) INPUT_REQUIRED: ask for extra seconds
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=genai_types.Content(
                    role='agent',
                    parts=[TextPart(text=json.dumps({
                        'input_required': True,
                        'requirements': 'Extra seconds you want me to sleep: '
                    }))]
                ),
                partial=False  # such that event.is_final_response is True
            )
        else:
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=genai_types.Content(
                    role='agent',
                    parts=[TextPart(text=json.dumps({
                        'result': 'Thank you for using this agent!'
                    }))]
                ),
                partial=False  # such that event.is_final_response is True
            )


class SleepingAgent:
    """
    Wrapper class for the sleeping agent
    """
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = "remote_agent"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def _build_agent(self):
        return InternalSleepingAgent(
            name="sleep_agent",
            description="Simulate sleeping with per-second progress and optional extra sleep."
        )

    async def stream(self, query, session_id):
        # print(f'[Debug] Received query: {query}')
        session = self._runner.session_service.get_session(
            app_name=self._agent.name, user_id=self._user_id, session_id=session_id
        )
        content = genai_types.Content(
            role="user", parts=[genai_types.Part.from_text(text=query)]
        )
        if session is None:
            session = self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={},
                session_id=session_id,
            )
        async for event in self._runner.run_async(
            user_id=self._user_id,
            session_id=session.id,
            new_message=content
        ):
            response = "\n".join([p.text for p in event.content.parts if p.text])
            if event.is_final_response():
                yield {
                    "is_task_complete": True,
                    "content": response,
                }
            else:
                yield {
                    "is_task_complete": False,
                    "updates": response,
                }
