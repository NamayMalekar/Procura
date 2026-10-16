"""App entry point.  Run from the backend/ folder:  uvicorn app.main:app --reload"""
import threading
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import data, evaluation, runs, scenarios, system
from app.core.config import settings
from app.core.exceptions import InvalidState, NotFound
from app.database.store import Store


def create_app(db_path=None):
    app = FastAPI(title=settings.app_name)
    app.state.store = Store.open(db_path or settings.database_path)

    # SQLite shares one connection, so handle one API call at a time.
    lock = threading.RLock()

    @app.middleware("http")
    async def one_at_a_time(request: Request, call_next):
        with lock:
            return await call_next(request)

    @app.exception_handler(NotFound)
    async def _nf(_, e):
        return JSONResponse({"detail": str(e)}, status_code=404)

    @app.exception_handler(InvalidState)
    async def _is(_, e):
        return JSONResponse({"detail": str(e)}, status_code=400)

    for r in (system.router, scenarios.router, runs.router, data.router, evaluation.router):
        app.include_router(r, prefix="/api")

    dist = settings.frontend_dist                      # built React app, if present
    if (dist / "index.html").exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str):
            f = dist / path
            return FileResponse(f if path and f.is_file() else dist / "index.html")
    return app


app = create_app()
