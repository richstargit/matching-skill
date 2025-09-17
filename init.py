import datetime
import json
import PyPDF2
import requests
from openai import OpenAI

import os
from dotenv import load_dotenv

from connect.connectGraphDB import connectGraph
from connect.connect_model import MODEL_RAG
from db.model_job import JobModel
from db.model_resume import ResumeModel
from prompt.prompt import PROMPT

from connect.connect_mongodb import resume_collection,job_collection

from collections import defaultdict

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

def add_job(tx, jobdata,mongodb_id):
    tx.run("""
        CREATE (j:Job {
            name: $name,
            mongodb_id: $mongodb_id
        })
    """, 
    name=jobdata['title'],
    mongodb_id=mongodb_id
    )

def add_relation_usertoskill(tx, user,skill):
    tx.run("""
        MATCH (c:Resume {name: $user})
        MATCH (s:Skill {name: $skill})
        MERGE (c)-[:HAVE_SKILL]->(s)
    """, user=user, skill=skill)

def add_relation_jobtoskill(tx, job,skill):
    tx.run("""
        MATCH (c:Job {mongodb_id: $job})
        MATCH (s:Skill {name: $skill})
        MERGE (c)-[:REQUIRED_SKILL]->(s)
    """, job=job, skill=skill)

def add_req_usertoexp(tx, mongodb_id,exp,exp_year):
    tx.run("""
        MATCH (c:Resume {mongodb_id: $mongodb_id})
        MATCH (s:Experience {name: $exp})
        MERGE (c)-[r:Experience_in]->(s)
        SET r.exp_year = $exp_year
    """, mongodb_id=mongodb_id, exp=exp,exp_year=exp_year)

def add_req_jobtoexp(tx, mongodb_id,exp,min_year,max_year):
    tx.run("""
        MATCH (c:Job {mongodb_id: $mongodb_id})
        MATCH (s:Experience {name: $exp})
        MERGE (c)-[r:REQUIRED_Experience]->(s)
        SET r.min_year = $min_year,
           r.max_year = $max_year
    """, mongodb_id=mongodb_id, exp=exp,min_year=min_year,max_year=max_year)

def add_req_usertoedu(tx, mongodb_id,edu):
    tx.run("""
        MATCH (c:Resume {mongodb_id: $mongodb_id})
        MATCH (s:Education {name: $edu})
        MERGE (c)-[:Education_in]->(s)
    """, mongodb_id=mongodb_id, edu=edu)

def add_req_jobtoedu(tx, mongodb_id,edu,edu_id,minimum_level):
    tx.run("""
        MATCH (c:Job {mongodb_id: $mongodb_id})
        MATCH (s:Education {name: $edu})
        MERGE (c)-[r:REQUIRED_Education]->(s)
        SET r.edu_id = $edu_id,
           r.minimum_level = $minimum_level
    """, mongodb_id=mongodb_id, edu=edu,edu_id=edu_id,minimum_level=minimum_level)

def add_skill(tx, skill_name, embedding):
    tx.run("""
        MERGE (s:Skill {name: $name})
        SET s.embedding = $embedding
    """, name=skill_name, embedding=embedding)

def add_exp(tx, exp, embedding):
    tx.run("""
        MERGE (s:Experience {name: $exp})
        SET s.embedding = $embedding
    """, exp=exp, embedding=embedding)

def add_edu(tx, edu, embedding):
    tx.run("""
        MERGE (s:Education {name: $edu})
        SET s.embedding = $embedding
    """, edu=edu, embedding=embedding)

def addUser(userdata):
    driver = connectGraph()

    #insert to mongodb
    resultdb = resume_collection.insert_one(ResumeModel.parse_obj(userdata).dict())

    #insert to graph
    with driver.session() as session:

        #create user node
        session.write_transaction(add_user, userdata['personalInfo']['email'],str(resultdb.inserted_id))

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

        #add exp
        for expdata in userdata['experiences']:
            exp = expdata["role"].lower()
            query_emb = model.encode([exp])[0].tolist()
            result = session.run("""
                CALL db.index.vector.queryNodes('experience_embedding_cos', $top_k, $embedding)
                YIELD node, score
                RETURN node.name AS name, score
            """, top_k=1, embedding=query_emb)
            result = list(result)

            start_year = int(expdata['startDate']['year'])
            if expdata.get('endDate') and expdata['endDate'].get('year'):
                end_year = int(expdata['endDate']['year'])
            else:
                now = datetime.datetime.now()
                end_year = now.year

            if len(result)==0:
                session.write_transaction(add_exp,exp,query_emb)
                session.write_transaction(add_req_usertoexp,str(resultdb.inserted_id),exp,end_year-start_year)
                continue

            matching = result[0]["name"]
            if float(result[0]["score"])<0.9:
                session.write_transaction(add_exp,exp,query_emb)
                matching = exp

            session.write_transaction(add_req_usertoexp,str(resultdb.inserted_id),matching,end_year-start_year)
        
        #add edu
        for edudata in userdata['education']:
            edu = edudata["major"].lower()
            query_emb = model.encode([edu])[0].tolist()
            result = session.run("""
                CALL db.index.vector.queryNodes('education_embedding_cos', $top_k, $embedding)
                YIELD node, score
                RETURN node.name AS name, score
            """, top_k=1, embedding=query_emb)
            result = list(result)

            if len(result)==0:
                session.write_transaction(add_edu,edu,query_emb)
                session.write_transaction(add_req_usertoedu,str(resultdb.inserted_id),edu)
                continue

            matching = result[0]["name"]
            if float(result[0]["score"])<0.9:
                session.write_transaction(add_edu,edu,query_emb)
                matching = edu

            session.write_transaction(add_req_usertoedu,str(resultdb.inserted_id),matching)
        

    driver.close()

def addJob(jobdata):
    driver = connectGraph()

    resultdb = job_collection.insert_one(JobModel.model_validate(jobdata).model_dump())

    with driver.session() as session:
        #create user node
        session.execute_write(add_job, jobdata,str(resultdb.inserted_id))

        #add skills
        for skill in jobdata['skills']:
            query_emb = model.encode([skill.lower()])[0].tolist()
            result = session.run("""
                CALL db.index.vector.queryNodes('skill_embedding_cos', $top_k, $embedding)
                YIELD node, score
                RETURN node.name AS name, score
            """, top_k=1, embedding=query_emb)
            result = list(result)
            if float(result[0]["score"])<0.8:
                # session.write_transaction(add_skill,skill,query_emb)
                # session.write_transaction(add_relation_jobtoskill,jobdata['title'],skill)
                continue
            session.execute_write(add_relation_jobtoskill,str(resultdb.inserted_id),result[0]["name"])

        #add exp

        for expdata in jobdata["experiences"]:
            exp = expdata["job_name"].lower()
            query_emb = model.encode([exp])[0].tolist()

            result = session.run("""
                CALL db.index.vector.queryNodes('experience_embedding_cos', $top_k, $embedding)
                YIELD node, score
                RETURN node.name AS name, score
            """, top_k=1, embedding=query_emb)
            result = list(result)

            min_year = int(expdata["min_experience_years"])
            if expdata["max_experience_years"]:
                max_year = int(expdata["max_experience_years"])
            else:
                max_year=min_year
            
            if len(result)==0:
                session.execute_write(add_exp,exp,query_emb)
                session.execute_write(add_req_jobtoexp,str(resultdb.inserted_id),exp,min_year,max_year)
                continue
                
            matching = result[0]["name"]
            if float(result[0]["score"])<0.9:
                session.execute_write(add_exp,exp,query_emb)
                matching = exp

            session.execute_write(add_req_jobtoexp,str(resultdb.inserted_id),matching,min_year,max_year)

        #add edu
        for edudata in jobdata['educations']:

            for edu in edudata["education"]:
                edu=edu.lower()
                query_emb = model.encode([edu])[0].tolist()
                result = session.run("""
                    CALL db.index.vector.queryNodes('education_embedding_cos', $top_k, $embedding)
                    YIELD node, score
                    RETURN node.name AS name, score
                """, top_k=1, embedding=query_emb)
                result = list(result)

                if len(result)==0:
                    session.execute_write(add_edu,edu,query_emb)
                    session.execute_write(add_req_jobtoedu,str(resultdb.inserted_id),edu,edudata["id"],edudata["minimum_level"])
                    continue

                matching = result[0]["name"]
                if float(result[0]["score"])<0.9:
                    session.execute_write(add_edu,edu,query_emb)
                    matching = edu

                session.execute_write(add_req_jobtoedu,str(resultdb.inserted_id),matching,edudata["id"],edudata["minimum_level"])


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


def find_resume_skill_by_mongodb_id(mongodb_id):
    driver = connectGraph()
    with driver.session() as session:
        result = session.run("""
                MATCH (:Resume {mongodb_id: $mongodb_id})-[:HAVE_SKILL*]->(s1:Skill)
                OPTIONAL MATCH (s1)-[:CHILD*]->(s3:Skill)
                OPTIONAL MATCH (s1)-[:RELATE*]->(s2:Skill)
                OPTIONAL MATCH (s2)-[:CHILD*]->(s4:Skill)
                WITH collect({parent:s1.name, child:s3.name}) +
                    collect({parent:s2.name, child:s4.name}) AS pairs,collect(s1.name) + collect(s2.name) AS allSkills
                UNWIND pairs AS pc
                WITH DISTINCT pc.parent AS parent, pc.child AS child, allSkills
                WHERE parent IS NOT NULL AND child IS NOT NULL
                RETURN apoc.coll.toSet(allSkills) AS skills,collect(child) AS childSkills;

            """, mongodb_id=mongodb_id)
        record = result.single()

    driver.close()
    return {
        "skills":record["skills"],
        "childSkills":record["childSkills"]
    }

def find_job_by_mongodb_id(mongodb_id):
    driver = connectGraph()
    with driver.session() as session:
        result = session.run("""
                MATCH (:Resume {mongodb_id: $mongodb_id})-[:HAVE_SKILL*]->(s1:Skill)
                OPTIONAL MATCH (s1)-[:RELATE*]->(s2:Skill)
                OPTIONAL MATCH (s1)-[:CHILD*]->(s3:Skill)
                OPTIONAL MATCH (s2)-[:CHILD*]->(s4:Skill)
                WITH collect(s1)+collect(s2)+collect(s3)+collect(s4) AS allSkills
                UNWIND allSkills AS skill
                MATCH (j:Job)-[:REQUIRED_SKILL]->(skill)
                WITH DISTINCT j 
                MATCH (j)-[:REQUIRED_SKILL]->(skill2:Skill)
                OPTIONAL MATCH (j)-[w:REQUIRED_Education]->(ej:Education)
                OPTIONAL MATCH (j)-[w2:REQUIRED_Experience]->(exp:Experience)
                RETURN j.name as name,j.mongodb_id as mongodb_id, collect(DISTINCT skill2.name) AS skills,
                collect(DISTINCT {exp_name:exp.name,max_year:w2.max_year,min_year:w2.min_year}) AS experiences,
                collect(DISTINCT {edu_id: w.edu_id, edu_name: ej.name, minimum_level: w.minimum_level}) AS educations;
            """, mongodb_id=mongodb_id)
    
        jobs = []
        for record in result:
            jobs.append({
                "name": record["name"],
                "mongodb_id": record["mongodb_id"],
                "skills": record["skills"],
                "experiences": record["experiences"],
                "educations": record["educations"]
            })

    driver.close()
    return jobs

def find_exp_edu_by_mongodb_id(mongodb_id):
    driver = connectGraph()
    with driver.session() as session:
        result = session.run("""
                MATCH p=(r:Resume {mongodb_id: $mongodb_id})-[w_exp:Experience_in]->(exp:Experience)
                OPTIONAL MATCH p2 = (r)-[:Education_in]->(edu:Education)
                RETURN r.name as name, collect(DISTINCT {name : exp.name,year:w_exp.exp_year}) as exp, collect(DISTINCT edu.name) as edu;
            """, mongodb_id=mongodb_id)
        
        record = result.single()

    driver.close()
    return {
        "exp":record["exp"],
        "edu":record["edu"]
    }

def score_edu_cal(j,resume_exp_edu):
    edu_dict = defaultdict(lambda: {"edu": set(), "min_level": ""})
    for edu in j["educations"]:
        edu_dict[edu["edu_id"]]["edu"].add(edu["edu_name"])
        edu_dict[edu["edu_id"]]["min_level"] = edu["minimum_level"]

    resume_edu_set = set(resume_exp_edu.get("edu", []))

    sum = 0
    matched = []
    not_matched = []

    for _, v in edu_dict.items():
        if v["edu"] & resume_edu_set:
            matched.extend(v["edu"] & resume_edu_set)  # เก็บเฉพาะที่ match
            sum+=1
        else:
            not_matched.extend(v["edu"])

    return sum / len(edu_dict) if edu_dict else 0.0,matched,not_matched

def score_exp_cal(j,exp_year):
    sum_exp = 0

    matched = []
    not_matched = []

    for exp in j["experiences"]:
        if exp["exp_name"] not in exp_year:
            not_matched.append(exp["exp_name"])

            continue
        if exp_year[exp["exp_name"]]>=exp["min_year"]:
            matched.append(exp["exp_name"])
            sum_exp+=0.6
        if exp_year[exp["exp_name"]]>=exp["max_year"]:
            sum_exp+=0.4
    
    return sum_exp/len(j["experiences"]),matched,not_matched

def score_job(email):
    result : ResumeModel = resume_collection.find_one({"personalInfo.email":email})
    mongodb_id = str(result["_id"])
    resume_skills = find_resume_skill_by_mongodb_id(mongodb_id)
    match_skills = {}

    for s in resume_skills["skills"]:
        match_skills[s]=1

    for s in resume_skills["childSkills"]:
        if s in match_skills:
            match_skills[s] += 0.2
        else:
            match_skills[s] = 0.5
        if match_skills[s] > 1:
            match_skills[s]=1

    resume_exp_edu = find_exp_edu_by_mongodb_id(mongodb_id)
    exp_year = {}

    for e in resume_exp_edu["exp"]:
        exp_year[e["name"]]=e["year"]

    jobs = find_job_by_mongodb_id(mongodb_id)
    
    job_score_dict = {}

    for j in jobs:
        match_all = len(j["skills"])
        ismatch = []
        isChild = []
        notmatch = []
        sum_skill = 0
        if len(j["skills"])==0:
            sum_skill=-1
        for s in j["skills"]:
            if s not in match_skills:
                notmatch.append(s)
                continue
            sum_skill+=match_skills[s]
            if match_skills[s]==1:
                ismatch.append(s)
            else:
                isChild.append(s)
        
        score_skill = (sum_skill/match_all)

        score_edu = -1
        matchedu=[]
        missedu=[]

        if j["educations"][0]["edu_name"]:
            score_edu,matchedu,missedu = score_edu_cal(j,resume_exp_edu)

        score_exp = -1
        matchexp=[]
        missexp=[]
        if j["experiences"][0]["exp_name"]:
            score_exp,matchexp,missexp = score_exp_cal(j,exp_year)

        job_score_dict[j["mongodb_id"]] = {
            "name":j["name"],
            "skill" :{
                "score":score_skill,
                "match":ismatch,
                "maybehave":isChild,
                "miss":notmatch
            },
            "experience":{
                "score":score_exp,
                "match":matchexp,
                "miss":missexp
            },
            "education":{
                "score":score_edu,
                "match":matchedu,
                "miss":missedu
            }
        }
    return job_score_dict

def cal_score(job_score):
    w_skill = 0.7
    w_exp = 0.2
    w_edu = 0.1

    w_list = [w_skill,w_exp,w_edu]
    cal_key = ["skill","experience","education"]

    for idx,k in enumerate(cal_key):
        if job_score[k]["score"]==-1:
            temp = w_list[idx]
            w_list[idx]=0
            for i in range(len(w_list)):
                if w_list[i]!=0:
                    w_list[i]+=temp
                    break

    score = w_list[0]*job_score["skill"]["score"]+w_list[1]*job_score["experience"]["score"]+w_list[2]*job_score["education"]["score"]

    return score

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