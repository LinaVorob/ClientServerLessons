import datetime
from sqlalchemy import Column, Integer, String, create_engine, DATETIME
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import ForeignKey


class ServerDB:

    Base = declarative_base()
    engine = create_engine('sqlite:///data.db', echo=False, pool_recycle=7200)

    class Users(Base):
        __tablename__ = 'users'
        id = Column(Integer(), primary_key=True)
        login = Column(String(), unique=True)
        last_enter = Column(DATETIME)

        def __init__(self, login):
            self.login = login
            self.last_enter = datetime.datetime.now()

        def __repr__(self):
            return f"<Client({self.login}, time: {self.last_enter})>"

    class ClientHistory(Base):
        __tablename__ = 'login_history'
        id = Column(Integer(), primary_key=True)
        user_port = Column(Integer())
        ip_address = Column(String(), nullable=False)
        user_id = Column(Integer(), ForeignKey('users.id'))
        login_time = Column(DATETIME)

        def __init__(self, user_id, ip_address, user_port):
            self.login_time = datetime.datetime.now()
            self.ip_address = ip_address
            self.user_id = user_id
            self.user_port = user_port

        def __repr__(self):
            return f"<Time = {self.login_time} by {self.ip_address}>"

    class ActiveUsers(Base):
        __tablename__ = 'list_of_client_online'
        id = Column(Integer(), primary_key=True)
        port = Column(Integer())
        ip_user = Column(String(), nullable=False)
        user_id = Column(Integer(), ForeignKey('users.id'))
        login_time = Column(DATETIME)

        def __init__(self, port, id_client, ip_user):
            self.port = port
            self.ip_user = ip_user
            self.login_time = datetime.datetime.now()
            self.user_id = id_client

        def __repr__(self):
            return f"User {self.ip_user} {self.port} enter in {self.login_time}"

    Base.metadata.create_all(engine)

    def __init__(self):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def login(self, username, ip, port):
        print(f'name = {username}, ip = {ip}, port = {port}')
        rez = self.session.query(self.Users).filter_by(login=username)
        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
            print(type(user))
        else:
            user = self.Users(username)
            self.session.add(user)
            self.session.commit()
            print(f'new {type(user)}')
        # new_active_user = self.ActiveUsers(port, user.id, ip)
        # self.session.add(new_active_user)
        # print(f'new_Active = {new_active_user}')
        history = self.ClientHistory(user.id, ip, port)
        self.session.add(history)
        print(f'history = {history}')
        self.session.commit()
        print('fin')

    def logout(self, username):
        user = self.session.query(self.Users).filter_by(login=username).first()
        print(type(user))
        self.session.query(self.ActiveUsers).filter_by(user_id=user.id).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(self.Users.login)
        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.Users.login,
            self.ActiveUsers.ip_user,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.Users)
        return query.all()

    def login_history(self, username=None):
        query = self.session.query(self.Users.login,
                                   self.ClientHistory.login_time,
                                   self.ClientHistory.ip_address,
                                   self.ClientHistory.user_port
                                   ).join(self.Users)
        if username:
            query = query.filter(self.Users.login == username)
        return query.all()

    def change_db(self, command, name):
        print(f'command = {command}, login = {name}')
        if command == 'add':
            print('in add')
            new_contact = self.Users(name)
            print(new_contact)
            self.session.add(new_contact)
            self.session.commit()
        elif command == 'del':
            print('in del')
            del_record = self.session.query(self.Users).filter_by(login=name).first()
            self.session.delete(del_record)
            self.session.commit()
        else:
            raise AttributeError

if __name__ == '__main__':
    test_db = ServerDB()
    # выполняем 'подключение' пользователя
    test_db.login('client_3', '192.168.1.10', 8888)
    test_db.login('client_2', '192.168.1.5', 7777)
    # выводим список кортежей - активных пользователей
    print(test_db.active_users_list())
    # выполянем 'отключение' пользователя
    test_db.logout('client_2')
    # выводим список активных пользователей
    print(test_db.active_users_list())
    # запрашиваем историю входов по пользователю
    test_db.login_history('client_1')
    # выводим список известных пользователей
    print(test_db.users_list())






