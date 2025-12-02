from .base import engine, SessionLocal, Base, get_db

def init_db():
    Base.metadata.create_all(bind=engine)
