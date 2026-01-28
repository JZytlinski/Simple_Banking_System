import logging
from fastapi import FastAPI, Request, logger
from fastapi.responses import JSONResponse
from app.core.database import Base, engine
from app.api.clients import router as clients_router
from app.api.managers import router as managers_router
from app.api.transactions import router as transactions_router
from app.api.persons import router as persons_router

Base.metadata.create_all(bind=engine)

logger = logging.getLogger("uvicorn.error")
app = FastAPI()


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.info(f"{request.url}: {exc}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(clients_router)
app.include_router(managers_router)
app.include_router(transactions_router)
app.include_router(persons_router)


@app.get("/")
def root():
    return {"status": "running"}
