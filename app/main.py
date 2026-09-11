from fastapi import FastAPI
from app.database import Base, engine, SessionLocal
from app.seed import seed_database
from app.middleware import TimingMiddleware
from app.routes import auth, dishes, orders

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Iya Ngozi's Kitchen API")

app.add_middleware(TimingMiddleware)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(dishes.router, prefix="/dishes", tags=["Dishes"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])


@app.get("/", tags=["Home"])
def home():
    return {"message": "Welcome to Iya Ngozi's Kitchen API"}


@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
