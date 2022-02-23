import datetime
from sqlalchemy import Column, Integer, String, create_engine, DATETIME
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import ForeignKey

engine = create_engine('sqlite:///data_client.db', echo=False)
pool_recycle = 7200

Base = declarative_base()


class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer(), primary_key=True)
    login = Column(String(), unique=True)
    info = Column(String())

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return f"<Contact({self.login}, {self.info})>"


class ChatHistory(Base):
    __tablename__ = 'history'
    id = Column(Integer(), primary_key=True)
    login_time = Column(DATETIME)
    to_contact = Column(Integer(), ForeignKey('contacts.id'))
    message = Column(String(), nullable=False)

    def __init__(self, to_contact, message):
        self.sending_time = datetime.datetime()
        self.to_contact = to_contact
        self.msg = message

    def __repr__(self):
        return f"Message <{self.msg}> to {self.to_contact} at {self.sending_time}"


Base.metadata.create_all(engine)
