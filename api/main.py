from fastapi import FastAPI

from routers import clients, phones, products, bills

app = FastAPI()

app.include_router(clients.router)
app.include_router(phones.router)
app.include_router(products.router)
app.include_router(bills.router)
