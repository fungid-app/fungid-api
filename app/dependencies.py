from db.models import core
from db.database import SessionLocal, engine

core.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
