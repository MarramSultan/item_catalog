#!/usr/bin/env python
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Create a Base class to be inhirited later by other code calss
Base = declarative_base()


# Looged in User info will be stored in the database
# The creator info of a country's category will be stored at Country table
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# Represent table country
# serilzation function to be used for JSON end point.
class Country(Base):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
              'name': self.name,
              'id': self.id,
              'creator_id': self.user_id
        }


# Represent table city_item
# serilzation function to be used for JSON end point.
class City(Base):
    __tablename__ = 'city_item'

    city = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    country_id = Column(Integer, ForeignKey('country.id'))
    country = relationship(Country)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
             'city': self.city,
             'description': self.description,
             'id': self.id,
             'country_id': self.country_id,
             'creator_id': self.user_id
        }


engine = create_engine('sqlite:///countries.db')

# Add the classes created as new tables in the Database
Base.metadata.create_all(engine)
