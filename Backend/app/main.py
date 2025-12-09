from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chan import router as chan_router
from app.routes.reddit import router as reddit_router
from app.routes.comparison import router as comparison_router

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