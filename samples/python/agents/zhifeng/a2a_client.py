import sys
import json
import asyncio

sys.path.append('../..')  # change it when necessary
from common.client import A2AClient, A2ACardResolver
from common.types import TaskState, SendTaskStreamingResponse


async def my_send_task(client, payload):
    async for update in client.send_task_streaming(payload):
        state = TaskState(update.result.status.state)
        data = json.loads(update.result.status.message.parts[0].text)
        if state == TaskState.INPUT_REQUIRED:
            extra = int(input(f"The agent asks: {data['requirements']}").strip())
            new_payload = {
                "id": "sleep-task-1",
                "sessionId": "session-1",
                "message": {"role": "user", "parts": [{"type": "text", "text": str(extra)}]},
            }
            await my_send_task(client, new_payload)
        elif state == TaskState.WORKING:
            print(f"The agent has slept for {data['elapsed']} seconds, "
                  f"leaving {data['remaining']} seconds before waking up")
        elif state == TaskState.COMPLETED:
            print("The agent finally says: ", data['result'])
            break


async def main():
    # 1) Discover the agent
    card = A2ACardResolver("http://localhost:20000").get_agent_card()  # change the port if necessary
    client = A2AClient(agent_card=card)
    print("Discovered agent:", card.name)

    init = int(input("Enter seconds to sleep: ").strip())
    payload = {
        "id": "sleep-task-1",
        "sessionId": "session-1",
        "message": {"role": "user", "parts": [{"type": "text", "text": str(init)}]},
    }
    await my_send_task(client, payload)


if __name__ == "__main__":
    asyncio.run(main())
