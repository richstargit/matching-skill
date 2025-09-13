from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("NEO4J_URL")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

def connectGraph():
    return GraphDatabase.driver(URL, auth=(USER, PASSWORD))