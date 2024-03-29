from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from contacts_book.conf.config import settings


# sql connection
SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    """
    The get_db function is a context manager that will automatically close the database session when it goes out of scope.
    It also handles any exceptions that occur within the with block, rolling back changes if necessary.
    
    :return: A database session object
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    finally:
        db.close()
