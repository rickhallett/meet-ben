from fastapi import FastAPI
from api.router import router as process_router

app = FastAPI()
app.include_router(process_router)
