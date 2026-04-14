from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.core.exceptions import AdPersonalizerError

app = FastAPI(
    title="Ad Personalizer API",
    description="Personalizes landing pages based on ad creative signals using Claude AI.",
    version="1.0.0",
)

settings = get_settings()

# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global error handler ────────────────────────────────────────────────────
@app.exception_handler(AdPersonalizerError)
async def app_error_handler(request: Request, exc: AdPersonalizerError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.message},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "An unexpected error occurred."},
    )

# ─── Routes ──────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}