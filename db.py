import atexit
from sqlalchemy import create_engine, Column, String, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from sqlalchemy_utils import EmailType, UUIDType
engine = create_engine("postgresql://andrey:990414@localhost:5432/netology")
Base = declarative_base()
Session = sessionmaker(bind=engine)
atexit.register(engine.dispose)


class Announcement(Base):
    __tablename__ = 'announcements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    creation_date = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('app_user.id', ondelete="CASCADE"))
    user = relationship("User", backref='owner_posts', foreign_keys=[user_id])

    def __repr__(self):
        return '<Announcement: {}>'.format(self.id)


class User(Base):
    __tablename__ = 'app_user'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    users_email = Column(EmailType, unique=True)
    token = Column(UUIDType, default=uuid.uuid4())

    def __repr__(self):
        return '<User: {}>'.format(self.username)


Base.metadata.create_all(bind=engine)
