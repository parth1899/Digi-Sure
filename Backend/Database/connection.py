from neo4j import GraphDatabase
from config import Config

class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def get_session(self):
        return self.driver.session()