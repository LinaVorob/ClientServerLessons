import datetime
from sqlalchemy import Column, Integer, String, create_engine, DATETIME
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import ForeignKey

engine = create_engine('sqlite:///data.db', echo=True)
pool_recycle = 7200

Base = declarative_base()


class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer(), primary_key=True)
    login = Column(String(), unique=True)
    info = Column(String())

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return f"<Client({self.login}, {self.info})>"


class ClientHistory(Base):
    __tablename__ = 'login_history'
    id = Column(Integer(), primary_key=True)
    login_time = Column(DATETIME)
    ip_address = Column(String(), nullable=False)

    def __init__(self, ip_address):
        self.login_time = datetime.datetime()
        self.ip_address = ip_address

    def __repr__(self):
        return f"<Time = {self.login_time} by {self.info}>"


class ClientsList(Base):
    __tablename__ = 'list_of_client'
    id = Column(Integer(), primary_key=True)
    id_owner = Column(Integer(), ForeignKey('clients.id'))
    id_client = Column(Integer(), ForeignKey('clients.id'))

    def __init__(self, id_o, id_c):
        self.id_owner = id_o
        self.id_client = id_c

    def __repr__(self):
        return f"<Owner({self.id_owner}) <-- Client({self.id_client})>"


Base.metadata.create_all(engine)
