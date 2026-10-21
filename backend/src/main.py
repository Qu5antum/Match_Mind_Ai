from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from src.core.config import settings
from src.exceptions_handlers.base_exception import BaseAppException
from src.api.endpoints.team_endpoint import team_route
from src.api.endpoints.player_endpoint import player_route
from src.api.endpoints.match_endpoint import match_route
from src.api.endpoints.match_event_endpoint import match_event_route
from src.api.endpoints.analytics_endpoint import analytics_route
from src.api.endpoints.match_insight_endpoint import match_insight_route
from src.api.endpoints.agent_endpoint import agent_route

logger = logging.getLogger("errors")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.debug,
    docs_url="/docs",
)

@app.exception_handler(BaseAppException)
async def app_exception_handler(request, exc):
    logger.error(
        "Unhandled exception",
        exc_info=True,
        extra={"path": request.url.path}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(team_route)
app.include_router(player_route)
app.include_router(match_route)
app.include_router(match_event_route)
app.include_router(analytics_route)
app.include_router(match_insight_route)
app.include_router(agent_route)


@app.get("/_info", status_code=200)
async def info():
    return {"app_name": settings.APP_NAME, "debug": settings.debug} 
