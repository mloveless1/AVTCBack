from sqlalchemy import create_engine
from .base import Base


def setup_database():
    engine = create_engine('mysql+pymysql://root:Iamnotmalo12!@localhost/avtc')
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    setup_database()
