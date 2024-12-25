from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_url = "postgresql://postgres:0000@localhost:5432/Jspace"

engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)
