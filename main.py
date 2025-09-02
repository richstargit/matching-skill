import json
import shutil
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
import os

from connectGraphDB import connectGraph
from init import addJob, addUser, extractData, extractJob, find_Job, readPDF, readPDFwithFile, score_qualifications

app = FastAPI()

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
    
    res = extractData(readData['data']).strip("`").replace("json", "", 1).strip()
    data = json.loads(res)
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
    res = extractJob(readData).strip("`").replace("json", "", 1).strip()
    data = json.loads(res)
    addJob(data)
    return {"isSuccess":True,  "result": data}


class Candidate(BaseModel):
    email:str
    
@app.post("/findjob")
async def addjob(candidate: Candidate):
    res = find_Job(candidate.email)
    if len(res)<0:
        return
    score = []
    score_q = json.loads(score_qualifications(candidate.email,res))
    score_qmap = {item['id']: item for item in score_q}
    for j in res:
        score_skill = len(j['match'])/(len(j['match'])+len(j['miss']))*100
    
        j['score_skill']=score_skill
        j['score_exp']=score_qmap[j['id']]['score_exp']
        j['score_edu']=score_qmap[j['id']]['score_edu']
        j['score'] = j['score_skill']*0.7+j['score_exp']*0.2+j['score_edu']*0.1
        score.append(j)
    return {"isSuccess":True,  "result": score}


@app.get("/jobs")
def get_jobs():
    driver = connectGraph()
    query = """
    MATCH (n:Job)-[:NEED_SKILL]->(s:Skill)
WITH n, collect(s.name) AS skills
RETURN {
    name: n.name,
    qualifications: n.qualifications,
    skills: skills
} AS job

    """

    jobs = []
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            jobs.append(record["job"])

    driver.close()

    return {"jobs": jobs}
