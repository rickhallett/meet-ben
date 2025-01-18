from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router as process_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process_router)
