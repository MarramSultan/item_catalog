from flask import session as login_session
from database_setup import Base, Country, City, User
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

# Connect to Database and create database session
engine = create_engine('sqlite:///countries.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one_or_none()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one_or_none()
        return user.id
    except BaseException:
        return None
