from db.database import engine
from sqlmodel import Session


def get_db():
    with Session(engine) as session:
        yield session
