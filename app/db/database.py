from decouple import config
from sqlmodel import create_engine

disk = str(config('DISK'))
db_file_name = str(config('DB_FILE_NAME'))

SQLALCHEMY_DATABASE_URL = "sqlite:///" + disk + db_file_name
print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
