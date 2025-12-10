from copilotkit import CopilotKitSDK, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
import json
import asyncio
from app.agent.sql_agent import sql_agent
from app.routes.chan import router as chan_router
from app.routes.comparison import router as comparison_router
from app.routes.reddit import router as reddit_router

app = FastAPI()

# Allow Next.js (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chan_router)
app.include_router(reddit_router)
app.include_router(comparison_router)

# CopilotKit SDK setup
sdk = CopilotKitSDK(
    agents=[
        LangGraphAgent(
            name="sql_agent",
            description="SQL agent for querying 4chan and Reddit data",
            graph=sql_agent,
        )
    ]
)

# Add CopilotKit endpoint
add_fastapi_endpoint(app, sdk, "/copilotkit")


async def stream_agent(graph, user_msg: str):
    """Helper: stream events from a LangGraph agent as SSE."""

    async def event_generator():
        initial_state = {"messages": [HumanMessage(content=user_msg)]}
        async for event in graph.stream(initial_state, stream_mode="updates"):
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/copilotkit/agent")
async def sql_stream(request: Request):
    body = await request.json()
    return await stream_agent(sql_agent, body.get("message", ""))


# add new route for health check
@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}
