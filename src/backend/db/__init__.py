from .session import get_db, engine
from .base import Base
from .models import Candidate, Job

def init_db():
    Base.metadata.create_all(bind=engine)
