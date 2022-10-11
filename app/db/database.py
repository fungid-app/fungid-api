from decouple import config
from sqlmodel import create_engine

db_file_name = str(config('DB_FILE_PATH'))

SQLALCHEMY_DATABASE_URL = "sqlite:///{}".format(db_file_name)
print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
