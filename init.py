import json
import PyPDF2
from openai import OpenAI

import os
from dotenv import load_dotenv
#from sentence_transformers import SentenceTransformer

from connectGraphDB import connectGraph
from prompt import PROMPT
load_dotenv()

TYPHOON_KEY = os.getenv("TYPHOON_KEY")
#model = SentenceTransformer('all-MiniLM-L6-v2')

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

def add_user(tx, userdata):
    tx.run("""
        MERGE (c:Candidate {name: $name})
        SET c.personalInfo = $personalInfo,
            c.experiences = $experiences,
            c.education = $education,
            c.certificates = $certificates,
            c.achievement = $achievement
    """,
    name=userdata['personalInfo']['email'],
    personalInfo=json.dumps(userdata['personalInfo']),
    experiences=json.dumps(userdata['experiences']),
    education=json.dumps(userdata['education']),
    certificates=json.dumps(userdata['certificates']),
    achievement=json.dumps(userdata['achievement'])
    )

def add_job(tx, jobdata):
    tx.run("""
        MERGE (j:Job {name: $name})
        SET j.qualifications = $qualifications
    """, name=jobdata['title'],qualifications=jobdata['qualifications'])

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


def addUser(userdata):
    driver = connectGraph()
    with driver.session() as session:
        #create user node
        session.write_transaction(add_user, userdata)

        #add skills
        for skill in userdata['skills']:
            # query_emb = model.encode([skill])[0].tolist()
            # result = session.run("""
            #     CALL db.index.vector.queryNodes('skill_embedding_cos', $top_k, $embedding)
            #     YIELD node, score
            #     RETURN node.name AS name, score
            # """, top_k=1, embedding=query_emb)
            # result = list(result)
            # if float(result[0]["score"])<0.75:
            #     continue

            session.write_transaction(add_relation_usertoskill,userdata['personalInfo']['email'],skill)
    driver.close()

def addJob(jobdata):
    driver = connectGraph()
    with driver.session() as session:
        #create user node
        session.write_transaction(add_job, jobdata)

        #add skills
        for skill in jobdata['skills']:
            # query_emb = model.encode([skill])[0].tolist()
            # result = session.run("""
            #     CALL db.index.vector.queryNodes('skill_embedding_cos', $top_k, $embedding)
            #     YIELD node, score
            #     RETURN node.name AS name, score
            # """, top_k=1, embedding=query_emb)
            # result = list(result)
            # if float(result[0]["score"])<0.75:
            #     continue

            session.write_transaction(add_relation_jobtoskill,jobdata['title'],skill)
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
            RETURN c.experiences AS experiences,c.education AS education
        """, name=name).single()
        if not record:
            return []
    experiences_json = record["experiences"]
    experiences = json.loads(experiences_json)
    education_json = record["education"]
    education = json.loads(education_json)
    res = extractScore_qualifications({"experiences":experiences,"education":education},[{"id":j["id"],"job":j["job"],"qualifications":j['qualifications']} for j in jobdata]).strip("`").replace("json", "", 1).strip()
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