from sqlmodel import create_engine, Session
import os

# Robustly find the database in the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = "baby_log.db"
DATABASE_PATH = os.path.join(BASE_DIR, DB_NAME)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session
