from fastapi import FastAPI
from app.database import init_db
from app.routers.transactions import router as transactions_router

app = FastAPI(title="Printing Management System")


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(transactions_router, prefix="/transactions", tags=["transactions"])


@app.get("/")
def root():
    return {"message": "Printing Management System API"}
