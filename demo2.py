from collections import defaultdict
from connect.connectGraphDB import connectGraph
from db.model_resume import ResumeModel
from connect.connect_mongodb import resume_collection


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

    matched_count = sum(1 for v in edu_dict.values() if v["edu"] & resume_edu_set)

    return matched_count / len(edu_dict) if edu_dict else 0.0

def score_exp_cal(j,exp_year):
    sum_exp = 0
    for exp in j["experiences"]:
        if exp["exp_name"] not in exp_year:
            continue
        if exp_year[exp["exp_name"]]>=exp["min_year"]:
            sum_exp+=0.6
        if exp_year[exp["exp_name"]]>=exp["max_year"]:
            sum_exp+=0.4
    
    return sum_exp/len(j["experiences"])



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
    
    for j in jobs:
        print(j["name"])
        match_all = len(j["skills"])
        sum_skill = 0
        for s in j["skills"]:
            if s not in match_skills:
                continue
            sum_skill+=match_skills[s]
        
        print("score skill :",(sum_skill/match_all)*100)
        if j["educations"][0]["edu_name"]:
            score = score_edu_cal(j,resume_exp_edu)

            print("score edu :",score*100)
        
        if j["experiences"][0]["exp_name"]:
            score = score_exp_cal(j,exp_year)
            print("score exp :",score*100)
        print("-----------------------------------")

score_job("johndoe@example.com")