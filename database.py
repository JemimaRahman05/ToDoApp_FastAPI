from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite://./todosapp.db"
#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root123@127.0.0.1:3306/todoapplicationdatabase"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()