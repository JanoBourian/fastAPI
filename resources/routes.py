from fastapi import APIRouter
from resources import register
from resources import login

api_router = APIRouter()

api_router.include_router(register.router)
api_router.include_router(login.router)
