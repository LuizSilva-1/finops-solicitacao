import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes import router as api_router
from app.db.session import SessionLocal
from app import models
from app.services import auth_service

app = FastAPI(title="FinOps Provisionamento Local")

logging.basicConfig(
    level=logging.INFO,
    format='{"level":"%(levelname)s","time":"%(asctime)s","message":"%(message)s"}',
)

app.include_router(api_router, prefix="/api")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return FileResponse("app/static/index.html")


@app.on_event("startup")
def seed_admin():
    db = SessionLocal()
    try:
        # Check if user table exists before seeding
        if engine_has_table(db, models.user.User.__tablename__):
            existing = db.query(models.user.User).filter(models.user.User.username == "admin").first()
            if not existing:
                admin = models.user.User(
                    username="admin",
                    password_hash=auth_service.hash_password("admin123"),
                    role="admin",
                    display_name="Administrador",
                )
                db.add(admin)
                db.commit()
    finally:
        db.close()


def engine_has_table(db, table_name: str) -> bool:
    try:
        return db.bind.has_table(table_name)  # type: ignore[attr-defined]
    except Exception:
        return False


@app.get("/admin")
def admin_page():
    return FileResponse("app/static/admin.html")
