import PyPDF2
from openai import OpenAI

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from connectGraphDB import connectGraph
from prompt import PROMPT
load_dotenv()

TYPHOON_KEY = os.getenv("TYPHOON_KEY")
model = SentenceTransformer('all-MiniLM-L6-v2')

def readPDF(path:str):
    try:
        with open(path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text=""
            # อ่านทีละหน้า
            for _, page in enumerate(reader.pages):
                text += page.extract_text()
        return  {"success": True, "data": text}
    except Exception:
        return {"success": False, "data": "error"}

def extractData(text:str):

    client = OpenAI(
        api_key=TYPHOON_KEY,
        base_url="https://api.opentyphoon.ai/v1"
    )

    messages = [
        {"role": "system", "content": PROMPT['extract_data']['system']},
        {"role": "user", "content": text}
    ]

    stream = client.chat.completions.create(
        model="typhoon-v2.1-12b-instruct",
        messages=messages,
        temperature=0.7,
        max_tokens=4096,
        top_p=0.9,
        stream=True
    )

    # Process the streaming response
    result = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            result += chunk.choices[0].delta.content
    return result

def add_user(tx, userdata):
    tx.run("""
        MERGE (c:Candidate {name: $name})
        SET c.email = $email
    """, name=userdata['personalInfo']['fullName'],email=userdata['personalInfo']['email'])

def add_relation_usertoskill(tx, user,skill):
    tx.run("""
        MATCH (c:Candidate {name: $user})
        MATCH (s:Skill {name: $skill})
        MERGE (c)-[:HAVE_SKILL]->(s)
    """, user=user, skill=skill)


def addUser(userdata):
    driver = connectGraph()
    with driver.session() as session:
        #create user node
        session.write_transaction(add_user, userdata)

        #add skills
        for skill in userdata['skills']:
            query_emb = model.encode([skill])[0].tolist()
            result = session.run("""
                CALL db.index.vector.queryNodes('skill_embedding_cos', $top_k, $embedding)
                YIELD node, score
                RETURN node.name AS name, score
            """, top_k=1, embedding=query_emb)
            result = list(result)
            if float(result[0]["score"])<0.75:
                continue

            session.write_transaction(add_relation_usertoskill,userdata['personalInfo']['fullName'],result[0]["name"])

