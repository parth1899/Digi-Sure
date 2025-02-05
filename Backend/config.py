from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    NEO4J_URI = os.getenv('NEO4J_URI')
    NEO4J_USER = os.getenv('NEO4J_USER')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour