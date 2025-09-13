import json
import PyPDF2
import requests
from openai import OpenAI

import os
from dotenv import load_dotenv

from connect.connectGraphDB import connectGraph
from connect.connect_model import MODEL_RAG
from db.model_resume import ResumeModel
from prompt.prompt import PROMPT

from connect.connect_mongodb import resume_collection

load_dotenv()

TYPHOON_KEY = os.getenv("TYPHOON_KEY")
GPTAPI = os.getenv("GPTAPI")
model = MODEL_RAG

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
    
def readPDFwithFile(file):
    try:
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

def extractData_GPT(text:str):

    prompt = "System :\n" + PROMPT['extract_data']['system'] + "\n\nUser Input:\n" + text

    url = GPTAPI
    payload = {
        "model": "gpt-oss:120b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    
    return response.json()["response"]

def extractJob(text:str):

    client = OpenAI(
        api_key=TYPHOON_KEY,
        base_url="https://api.opentyphoon.ai/v1"
    )

    messages = [
        {"role": "system", "content": PROMPT['extract_job']['system']},
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

def extractJob_GPT(text:str):

    prompt = "System :\n" + PROMPT['extract_job']['system'] + "\n\nUser Input:\n" + text

    url = GPTAPI
    payload = {
        "model": "gpt-oss:120b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    
    return response.json()["response"]

def add_user(tx, email,mongodb_id):
    tx.run("""
        CREATE (r:Resume {
            name: $name,
            mongodb_id: $resume_id
        })
    """,
    name=email,
    resume_id = mongodb_id
    )

def add_job(tx, jobdata):
    tx.run("""
        CREATE (j:Job {
            name: $name,
            qualifications: $qualifications
        })
    """, 
    name=jobdata['title'],
    qualifications=jobdata['qualifications'])

def add_relation_usertoskill(tx, user,skill):
    tx.run("""
        MATCH (c:Candidate {name: $user})
        MATCH (s:Skill {name: $skill})
        MERGE (c)-[:HAVE_SKILL]->(s)
    """, user=user, skill=skill)

def add_relation_jobtoskill(tx, job,skill):
    tx.run("""
        MATCH (c:Job {name: $job})
        MATCH (s:Skill {name: $skill})
        MERGE (c)-[:NEED_SKILL]->(s)
    """, job=job, skill=skill)

def add_skill(tx, skill_name, embedding):
    tx.run("""
        MERGE (s:Skill {name: $name})
        SET s.embedding = $embedding
    """, name=skill_name, embedding=embedding)

def addUser(userdata):
    driver = connectGraph()

    #insert to mongodb
    result = resume_collection.insert_one(ResumeModel.parse_obj(userdata).dict())

    #insert to graph
    with driver.session() as session:

        #create user node
        session.write_transaction(add_user, userdata['personalInfo']['email'],str(result.inserted_id))

        #add skills
        for skill in userdata['skills']:
            query_emb = model.encode([skill.lower()])[0].tolist()
            result = session.run("""
                CALL db.index.vector.queryNodes('skill_embedding_cos', $top_k, $embedding)
                YIELD node, score
                RETURN node.name AS name, score
            """, top_k=1, embedding=query_emb)
            result = list(result)
            if float(result[0]["score"])<0.8:
                # session.write_transaction(add_skill,skill,query_emb)
                # session.write_transaction(add_relation_usertoskill,userdata['personalInfo']['email'],skill)
                continue

            session.write_transaction(add_relation_usertoskill,userdata['personalInfo']['email'],result[0]["name"])
    driver.close()

def addJob(jobdata):
    driver = connectGraph()
    with driver.session() as session:
        #create user node
        session.write_transaction(add_job, jobdata)

        #add skills
        for skill in jobdata['skills']:
            query_emb = model.encode([skill.lower()])[0].tolist()
            result = session.run("""
                CALL db.index.vector.queryNodes('skill_embedding_cos', $top_k, $embedding)
                YIELD node, score
                RETURN node.name AS name, score
            """, top_k=1, embedding=query_emb)
            result = list(result)
            if float(result[0]["score"])<0.75:
                # session.write_transaction(add_skill,skill,query_emb)
                # session.write_transaction(add_relation_jobtoskill,jobdata['title'],skill)
                continue

            session.write_transaction(add_relation_jobtoskill,jobdata['title'],result[0]["name"])
    driver.close()

def find_Job(name):
    driver = connectGraph()
    with driver.session() as session:
        result = session.run("""
                WITH $name AS candidateName
                CALL (candidateName) {
                    WITH candidateName
                    MATCH (c:Candidate {name: candidateName})-[:HAVE_SKILL]->(s:Skill)<-[:NEED_SKILL]-(j:Job)
                    OPTIONAL MATCH (sj:Skill)<-[:NEED_SKILL]-(j)
                    RETURN j.name AS job, collect(DISTINCT sj.name) AS need_skills,j.qualifications AS qualifications
                    UNION
                    WITH candidateName
                    MATCH (c:Candidate {name: candidateName})-[:HAVE_SKILL]->(s:Skill)-[:HAS_SKILL*]->(sub:Skill)<-[:NEED_SKILL]-(j:Job)
                    OPTIONAL MATCH (sj:Skill)<-[:NEED_SKILL]-(j)
                    RETURN j.name AS job, collect(DISTINCT sj.name) AS need_skills,j.qualifications AS qualifications
                }
                RETURN job, need_skills,qualifications
                LIMIT 1000
            """, name=name)
        
        candidate = session.run("""
                MATCH (c:Candidate {name: $name})-[:HAVE_SKILL]->(s:Skill)
                OPTIONAL MATCH (s)-[:HAS_SKILL*]->(s2:Skill)
                RETURN c.name AS candidate, collect(DISTINCT s.name) + collect(DISTINCT s2.name) AS skills
            """, name=name)
        jobs = []
        candidate = list(candidate)
        if len(candidate)<0:
            return jobs
        candidate_skill = candidate[0]['skills']
        i=0
        for row in result:
            i+=1
            match_skill = []
            miss_skill = []
            for s in row["need_skills"]:
                if s in candidate_skill:
                    match_skill.append(s)
                else:
                    miss_skill.append(s)
            jobs.append({
                "id":i,
                "job": row["job"],
                "match": match_skill,
                "miss": miss_skill,
                "qualifications":row["qualifications"]
            })
    driver.close()
    return jobs

def score_qualifications(name,jobdata):
    driver = connectGraph()
    with driver.session() as session:
        record = session.run("""
            MATCH (c:Candidate {name: $name})
            RETURN c.experiences AS experiences,c.education AS education,c.achievement AS achievement
        """, name=name).single()
        if not record:
            return []
    experiences_json = record["experiences"]
    experiences = json.loads(experiences_json)
    education_json = record["education"]
    education = json.loads(education_json)
    achievement_json = record['achievement']
    achievement = json.loads(achievement_json)
    res = extractScore_qualifications_GPT({"experiences":experiences,"education":education,"achievement":achievement},[{"id":j["id"],"job":j["job"],"qualifications":j['qualifications']} for j in jobdata]).strip("`").replace("json", "", 1).strip()
    driver.close()
    return res

def extractScore_qualifications(Candidate_data,job_data):
    client = OpenAI(
        api_key=TYPHOON_KEY,
        base_url="https://api.opentyphoon.ai/v1"
    )

    messages = [
        {"role": "system", "content": PROMPT['extractScore_qualifications']['system']},
        {"role": "user", "content": '''
Candidate_data: {}
job_data : {}
'''.format(Candidate_data,job_data)}
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

def extractScore_qualifications_GPT(Candidate_data,job_data):

    prompt = "System :\n" + PROMPT['extractScore_qualifications']['system'] + "\n\nUser Input:\n" + "Candidate_data: {}\njob_data : {}".format(Candidate_data,job_data)

    url = GPTAPI
    payload = {
        "model": "gpt-oss:120b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    
    return response.json()["response"]