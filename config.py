import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/prestamos_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
