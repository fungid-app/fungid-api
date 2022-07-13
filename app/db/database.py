from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config


disk = str(config('DISK'))
db_file_name = str(config('DB_FILE_NAME'))

SQLALCHEMY_DATABASE_URL = "sqlite:///" + disk + db_file_name
print(SQLALCHEMY_DATABASE_URL)
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
