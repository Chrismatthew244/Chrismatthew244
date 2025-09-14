from sqlalchemy import Column, Integer, String

from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    path = Column(String, unique=True, index=True)
    customer = Column(String, index=True)
    task = Column(String, index=True)
