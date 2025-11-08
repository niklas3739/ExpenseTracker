from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from expense_tracker.core.db import init_db
from expense_tracker.api.routes.groups import router as groups_router
from expense_tracker.api.routes.expenses import router as expenses_router
from expense_tracker.api.routes.settlements import router as settlements_router
from expense_tracker.api.routes.balance import router as balance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Group Expense Tracker", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(groups_router)
    app.include_router(expenses_router)
    app.include_router(settlements_router)
    app.include_router(balance_router)

    return app


app = create_app()
