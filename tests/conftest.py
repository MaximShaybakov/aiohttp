import pytest
from datetime import datetime
from models import Base, User
from config import PG_DB, PG_PORT, PG_HOST, PG_USER, PG_PASSWORD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import hash_password


engine = create_engine(f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}')
Session = sessionmaker(bind=engine)


@pytest.fixture(scope='session', autouse=True)
def cleanup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope='session')
def root_user():
    with Session() as session:
        new_user = User(name='root', admin=True, password=hash_password('toor'), email='root@mail.ru')
        session.add(new_user)
        session.commit()
        return {
            'id': new_user.id,
            'name': new_user.name,
            'admin': new_user.admin,
            'password': 'toor',
            'email': new_user.email
        }


@pytest.fixture(scope='session', autouse=True)
def new_user():
    with Session() as session:
        new_user = User(name=f'gorshok_{datetime.now().time()}',
                        admin=False,
                        password=hash_password('iamgorshenyov'),
                        email='king&jester@mail.ru')
        session.add(new_user)
        session.commit()
        return {
            'id': new_user.id,
            'name': new_user.name,
            'admin': new_user.admin,
            'password': 'iamgorshenyov',
            'email': new_user.email
        }
