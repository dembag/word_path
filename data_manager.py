""" Interactions with the database"""

import os
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship, DeclarativeBase

# get path to word_path folder
basedir = os.path.abspath(os.path.dirname(__file__))

# Create database connection
engine = create_engine(f"sqlite:///{os.path.join(basedir, 'data/word_path.db')}")

# Create session factory
Session = sessionmaker(authcommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Generates sessions for routes
def get_db():
    with Session() as db:
        yield db