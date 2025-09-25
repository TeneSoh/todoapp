from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./usersapp.db'
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:lyonnel@localhost:5432/todoApp'
SQLALCHEMY_DATABASE_URL = 'postgresql://usersapp_user:bZ72Oa4aZ8VQo5lLxVlIewJwnowaUtvk@dpg-d3alom8dl3ps73eufkrg-a/usersapp'

# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread':False})
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()