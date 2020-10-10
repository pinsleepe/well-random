from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_NAME = os.environ.get('POSTGRES_NAME')
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")


class PSQLDatabase(object):
    """
    PSQL Database class to ease querys, opening and closing
    """

    def __init__(self):

        self.master_db_name = POSTGRES_NAME
        self.database_port = POSTGRES_PORT
        self.database_server = POSTGRES_HOST
        self.user = POSTGRES_USER
        self.pwd = POSTGRES_PASSWORD

        postgres_db = {'drivername': 'postgres',
                       'username': self.user,
                       'password': self.pwd,
                       'host': self.database_server,
                       'port': self.database_port,
                       'database': self.master_db_name}

        self.postgres_db = postgres_db
        self.engine = create_engine(URL(**postgres_db))


db = PSQLDatabase()
