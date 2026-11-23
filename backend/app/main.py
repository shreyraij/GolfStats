from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.players import router as players_router
from app.api.rankings import router as rankings_router

app = FastAPI(title="GolfStats API")

# Frontend dev server runs on a different origin (Vite on :5173, API on
# :8000); without this the browser blocks every request as cross-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(rankings_router)
app.include_router(players_router)


@app.get("/health")
def health():
    return {"status": "ok"}
