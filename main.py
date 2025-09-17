import json
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from connect.connectGraphDB import connectGraph
from init import addJob, addUser, cal_score, extractData_GPT, extractJob_GPT, readPDFwithFile, score_job

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GET API
@app.get("/")
def read_root():
    return {"message": "Hello"}

@app.post("/addcandidate")
async def AddCandidate(file: UploadFile = File(...)):
    # ตรวจสอบนามสกุลไฟล์
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    readData = readPDFwithFile(file.file)
    if not readData['success']:
        return {"isSuccess":False}
    
    res = extractData_GPT(readData['data']).strip("`").replace("json", "", 1).strip()
    data = json.loads(res)
    with open("log_resume.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    addUser(data)

    return {"isSuccess":True,  "result": data}


class JobRequest(BaseModel):
    jobTitle: str
    description: str

@app.post("/addjob")
async def add_job(job: JobRequest):
    readData = '''
job:{}
description:{}
'''.format(job.jobTitle,job.description)
    res = extractJob_GPT(readData).strip("`").replace("json", "", 1).strip()
    data = json.loads(res)
    addJob(data)
    return {"isSuccess":True,  "result": data}


class Candidate(BaseModel):
    email:str
    
@app.post("/findjob")
async def addjob(candidate: Candidate):
    job_dict = score_job(candidate.email)
    for key,job in job_dict.items():
        job_dict[key]["score"] = round(cal_score(job),2)
    
    job_list = []
    for key, job in job_dict.items():
        job_list.append({"id": key, **job})
    return {"isSuccess":True,  "result": job_list}

# @app.post("/findjob")
# async def addjob(candidate: Candidate):
#     res = find_Job(candidate.email)
#     if len(res)<0:
#         return
#     score = []
#     score_q = json.loads(score_qualifications(candidate.email,res))
#     score_qmap = {item['id']: item for item in score_q}
#     for j in res:
#         score_skill = len(j['match'])/(len(j['match'])+len(j['miss']))*100
    
#         j['score_skill']=score_skill
#         j['score_exp']=score_qmap[j['id']]['score_exp']
#         j['score_edu']=score_qmap[j['id']]['score_edu']
#         j['score_ach']=score_qmap[j['id']]['score_ach']
#         j['exp_reasons'] = score_qmap[j['id']].get('exp_reasons', [])
#         j['edu_reasons'] = score_qmap[j['id']].get('edu_reasons', [])
#         j['ach_reasons'] = score_qmap[j['id']].get('ach_reasons', [])

#         score_min = min(j['score_skill'], j['score_exp'], j['score_edu'])

#         if j['score_skill']== score_min:
#             j['score_skill']+=j['score_ach']*0.1
#             if j['score_skill']>100:
#                 j['score_skill']=100
#         elif j['score_exp']== score_min:
#             j['score_exp']+=j['score_ach']*0.1
#             if j['score_exp']>100:
#                 j['score_exp']=100
#         else :
#             j['score_edu']+=j['score_ach']*0.1
#             if j['score_edu']>100:
#                 j['score_edu']=100

#         j['score'] = j['score_skill']*0.7+j['score_exp']*0.2+j['score_edu']*0.1
#         score.append(j)
#     return {"isSuccess":True,  "result": score}


@app.get("/jobs")
def get_jobs():
    driver = connectGraph()
    query = """
    MATCH (j:Job)-[:REQUIRED_SKILL]->(skill2:Skill)
    OPTIONAL MATCH (j)-[w:REQUIRED_Education]->(ej:Education)
    OPTIONAL MATCH (j)-[w2:REQUIRED_Experience]->(exp:Experience)
    RETURN j.name as name,
           j.mongodb_id as mongodb_id,
           collect(DISTINCT skill2.name) AS skills,
           collect(DISTINCT {exp_name:exp.name, max_year:w2.max_year, min_year:w2.min_year}) AS experiences,
           collect(DISTINCT {edu_id: w.edu_id, edu_name: ej.name, minimum_level: w.minimum_level}) AS educations;
    """

    jobs = []
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            jobs.append({
                "name": record["name"],
                "mongodb_id": record["mongodb_id"],
                "skills": record["skills"],
                "experiences": record["experiences"],
                "educations": record["educations"]
            })

    driver.close()

    return {"jobs": jobs}

@app.get("/candidate")
def getCandidate():
    driver = connectGraph()
    query = """
    MATCH (c:Candidate)
OPTIONAL MATCH (c)-[:HAVE_SKILL]->(s:Skill)
OPTIONAL MATCH (s)-[:HAS_SKILL*]->(related:Skill)
WITH c, collect(DISTINCT s.name) + collect(DISTINCT related.name) AS skills
RETURN c.name AS name, skills,
       coalesce(c.experiences, '[]') AS experiences,
       coalesce(c.education, '[]') AS education,
       coalesce(c.certificates, '[]') AS certificates,
       coalesce(c.achievement, '[]') AS achievements,
       coalesce(c.personalInfo, '{}') AS personalInfo
    """
    
    candidates = []
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            candidates.append({
                "name": record["name"],
                "skills": record["skills"],  # skills จาก relation
                "experiences": json.loads(record["experiences"]) if record["experiences"] else [],
                "education": json.loads(record["education"]) if record["education"] else [],
                "certificates": json.loads(record["certificates"]) if record["certificates"] else [],
                "achievements": json.loads(record["achievements"]) if record["achievements"] else [],
                "personalInfo": json.loads(record["personalInfo"]) if record["personalInfo"] else {}
            })
    driver.close()
    return {"candidates": candidates}
    
