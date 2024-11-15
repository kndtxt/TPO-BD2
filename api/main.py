from fastapi import FastAPI

from .routers import clients, phones

app = FastAPI()

app.include_router(clients.router)
app.include_router(phones.router)
