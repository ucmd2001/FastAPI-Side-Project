from configs.settings import get_settings
from fastapi import APIRouter
from apps.plan_cart.api import plan_cart_router

runtime_settings = get_settings()

routers = APIRouter(prefix=runtime_settings.HOME_URL)


@routers.get("/")
def home():
    """home url"""
    return {"message": "You're in Home, Welcome"}


@routers.get("/Ping")
def simple_healthcheck():
    """simple healthcheck"""
    return {"Ping": "Pong🏓 v0.0.1"}


routers.include_router(plan_cart_router)
