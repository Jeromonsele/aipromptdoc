from db import SessionLocal, init_db
from typing import Generator

# create tables on import
init_db()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
