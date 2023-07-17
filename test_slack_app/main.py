import os
import settings

from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

# load dotenv if exists
settings.load_dotenv()

# Create an Async Bolt App instance
app = AsyncApp(
        token=os.environ["SLACK_BOT_TOKEN"],
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
        )
handler = AsyncSlackRequestHandler(app)

# Create a FastAPI instance
fastapi_app = FastAPI()


@fastapi_app.post("/slack/events")
async def endpoint(req: Request):
    return await handler.handle(req)


@fastapi_app.get("/ping")
async def ping():
    return {"message": "pong"}


# Register a listener for incoming messages
@app.message("hello")
async def message_hello(message, say):
    await say(f"Hey there <@{message['user']}>!")


def run_locally():
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "api":
        import uvicorn

        uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
    # otherwise, run the slack app in socket mode
    else:
        import asyncio

        from slack_bolt.adapter.socket_mode.async_handler import \
            AsyncSocketModeHandler

        async def run():
            handler = AsyncSocketModeHandler(
                app, app_token=os.environ["SLACK_APP_TOKEN"]
            )
            await handler.start_async()

        asyncio.run(run())


if __name__ == "__main__":
    run_locally()
