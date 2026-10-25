from fastapi import APIRouter
from app.api.resumes import router as resumes_router
from app.api.analyses import router as analyses_router
from app.api.questions import router as questions_router
from app.api.evaluations import router as evaluations_router
from app.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(resumes_router)
api_router.include_router(analyses_router)
api_router.include_router(questions_router)
api_router.include_router(evaluations_router)
