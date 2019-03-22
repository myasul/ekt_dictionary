from sqlalchemy import Column, Integer, String, func, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship

Base = declarative_base()


class Dictionary(Base):
    __tablename__ = 'dictionary'

    kapampangan = Column(String(250), primary_key=True)
    tagalog = Column(String(250), primary_key=True)
    english = Column(String(250), nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())


engine = create_engine('sqlite:///ekt_dictionary.db')

Base.metadata.create_all(engine)
