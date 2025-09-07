import json
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from connectGraphDB import connectGraph
from init import addJob, addUser, extractData, extractJob, find_Job, readPDF, readPDFwithFile, score_qualifications

app = FastAPI()

origins = [
    "*"  # หรือใส่เฉพาะโดเมน เช่น "http://localhost:3000", "https://996964f0140c.ngrok-free.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # อนุญาตโดเมนไหนเข้าถึง API
    allow_credentials=True,
    allow_methods=["*"],             # อนุญาต method GET, POST, PUT, DELETE
    allow_headers=["*"],             # อนุญาต headers ทั้งหมด
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
        j['exp_reasons'] = score_qmap[j['id']].get('exp_reasons', [])
        j['edu_reasons'] = score_qmap[j['id']].get('edu_reasons', [])
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
    
