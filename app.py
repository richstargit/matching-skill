import json
from init import addJob, addUser, extractData, extractJob, find_Job, readPDF, score_qualifications

def candidateJoin():
    readData = readPDF("dataset/resume/Backend_Developer_Resume.pdf")
    if not readData['success']:
        return
    
    res = extractData(readData['data']).strip("`").replace("json", "", 1).strip()
    data = json.loads(res)
    addUser(data)

def jobJoin():
    readData = '''
Company: CloudWorks Solutions
Location: Remote (Work from anywhere)
Employment Type: Full-time
Level: Mid-Level
Salary: 45,000 – 70,000 THB/month (based on experience)
Benefits:
Remote work allowance
Health & wellness package
Paid annual leave + national holidays
Performance-based bonus
Laptop and equipment provided
Job Summary:
As a Backend Developer at CloudWorks Solutions, you will be responsible for building and maintaining scalable backend systems to support our enterprise cloud solutions. You will work with cross-functional teams to design APIs, manage databases, and optimize performance.
Responsibilities:
Design, develop, and maintain backend systems using Node.js and Python
Build and document RESTful and GraphQL APIs
Manage and optimize databases (MongoDB, PostgreSQL)
Implement security and data protection best practices
Deploy applications using Docker and cloud services (AWS, GCP, Azure)
Collaborate with frontend and DevOps teams to deliver high-quality software
Requirements (Must-have):
Bachelor’s degree in Computer Science, Information Technology, or related field
2+ years of experience in backend development with Node.js or Python
Proficiency in database design and query optimization (SQL/NoSQL)
Experience with Git and version control workflows
Knowledge of software development lifecycle (SDLC)
Nice-to-have:
Experience with Docker, Kubernetes, or other containerization tools
Familiarity with CI/CD pipelines (Jenkins, GitHub Actions, GitLab CI)
Knowledge of microservices architecture
Previous experience with Agile methodology
Closing Date: October 15, 2025
How to Apply: Submit your resume and cover letter to jobs@cloudworks.io
    '''

    res = extractJob(readData).strip("`").replace("json", "", 1).strip()
    data = json.loads(res)
    addJob(data)

def findJob(name):
    res = find_Job(name)
    if len(res)<0:
        return
    score = []
    score_q = json.loads(score_qualifications(name,res))
    score_qmap = {item['id']: item for item in score_q}
    for j in res:
        score_skill = len(j['match'])/(len(j['match'])+len(j['miss']))*100
    
        j['score_skill']=score_skill
        j['score_exp']=score_qmap[j['id']]['score_exp']
        j['score_edu']=score_qmap[j['id']]['score_edu']
        j['score'] = j['score_skill']*0.7+j['score_exp']*0.2+j['score_edu']*0.1
        score.append(j)
    
    for s in score:
        print(s['job'])
        print(s['score'])
        print('---------------------')

    


def main():
    while(1):
        c = input("key:")
        if c=='1':
            candidateJoin()
        elif c=='2':
            jobJoin()
        else:
            findJob("daniel.lee@email.com")

    return

main()
