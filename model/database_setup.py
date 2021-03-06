from sqlalchemy import Column, Integer, String, func, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship

Base = declarative_base()


class Dictionary(Base):
    __tablename__ = "dictionary"

    kapampangan = Column(String(250), primary_key=True)
    tagalog = Column(String(250), primary_key=True)
    english = Column(String(250), primary_key=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())


class QueryResultMaintainer(Base):
    __tablename__ = "query_result_maintainer"

    screen_id = Column(Integer, ForeignKey("screens.id"), primary_key=True)
    direction = Column(Integer, ForeignKey("scroll_direction.id"), primary_key=True)
    next_row = Column(Integer, nullable=False)
    total_rows = Column(Integer, nullable=False)


class ScrollDirection(Base):
    __tablename__ = "scroll_direction"

    id = Column(Integer, primary_key=True)
    description = Column(String(50), nullable=False)


class SearchFilter(Base):
    __tablename__ = "search_filter"

    screen_id = Column(Integer, ForeignKey("screens.id"), primary_key=True)
    search_str = Column(String(250), nullable=False)
    search_mode = Column()
    language = Column()


class Screens(Base):
    __tablename__ = "screens"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(250))


engine = create_engine("sqlite:///model/ekt_dictionary.db")

Base.metadata.create_all(engine)
