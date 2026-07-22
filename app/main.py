from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from app.api.v1.career_router import router as career_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Career Mentor Agent API",
        description="Production schema-first AI Career Mentorship application.",
        version="1.0.0"
    )

    app.include_router(career_router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> HTMLResponse:
        error_messages = "<br>".join([f"• {err.get('msg')} at {err.get('loc')}" for err in exc.errors()])
        return HTMLResponse(
            status_code=422,
            content=f"""
            <html>
                <body style="background:#020617; color:white; font-family:Arial; padding:40px;">
                    <div style="max-width:600px; margin:auto; background:rgba(239, 68, 68, 0.1); border:1px solid #ef4444; padding:30px; border-radius:16px;">
                        <h2>⚠️ Invalid Input Details</h2>
                        <p>{error_messages}</p>
                        <a href="/" style="color:#38bdf8; display:inline-block; margin-top:20px;">⬅ Back to Form</a>
                    </div>
                </body>
            </html>
            """
        )

    return app


app: FastAPI = create_app()
