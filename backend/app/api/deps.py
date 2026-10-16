from fastapi import Request
from app.services.run_service import RunService


def get_store(request: Request):
    return request.app.state.store


def get_run_service(request: Request):
    return RunService(request.app.state.store)
