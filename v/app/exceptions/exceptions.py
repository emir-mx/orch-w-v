import logging
from . import status


class ConnectionException(Exception):
    def __init__(self, status_code, host):
        self.status = status_code
        self.host = host
        logging.error(f"Connection fail code {self.status}, Host {self.host}")


class DBException(Exception):
    def __init__(self, status_code, db_url):
        self.status = status_code
        self.url = db_url
        logging.error(f"DB Connection fail code {self.status}, URL {self.url}")