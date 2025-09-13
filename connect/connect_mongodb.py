from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB = os.getenv("MONGODB")

client = MongoClient(MONGODB)
db = client['jobmatchDB']
resume_collection = db['resumes']