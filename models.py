from sqlalchemy import Column, Integer, String, DateTime, Text, \
    create_engine, func, Boolean
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from config import PG_DSN


engine = create_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    admin = Column(Boolean)
    creation_time = Column(DateTime, server_default=func.now())
    password = Column(String(60), nullable=False)
    email = Column(String(30), nullable=True)
    advertisements = relationship('Ads', back_populates="owner")


class Token(Base):

    __tablename__ = 'tokens'

    id = Column(UUID, primary_key=True, server_default=func.uuid_generate_v4())
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('User', lazy='joined')
    created = Column(DateTime, server_default=func.now())


class Ads(Base):

    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True)
    title = Column(String(30), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates="advertisements")

    def __repr__(self):
        return f'Ads "{self.title[:20]}"'