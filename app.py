import json
from init import addJob, addUser, extractData, extractJob, find_Job, readPDF, score_qualifications

def candidateJoin():
    readData = readPDF("dataset/resume/FullStack_Resume.pdf")
    if not readData['success']:
        return
    
    res = extractData(readData['data']).strip("`").replace("json", "", 1).strip()
    data = json.loads(res)
    addUser(data)

def jobJoin():
    readData = '''
Back-end / Full Stack Developer (Golang)
Responsibilities :
 To analysis requirement, identify system impact, design solutions, and transform to technical task specification that support efficient and effective business operation work.  
Closely working with business users to understand business needs, provide consultant and support. 
To lead architecture system design for business enhancement and fixing any production issues with ensure the system performance and stability.    
To lead system analyst/full stack developer include design, coding, testing and prepare deployment. 
To help the team with problem solving on any technical issues. 
To design, coding and testing the application programs. 
To support production, investigate and fix any issues. 
Qualifications :
Bachelor's Degree / Master's Degree (IT, Computer Engineering, Computer Science, MBA, Economics, or related fields.)
2-5 years’ experience in system analyst, and/or development. 
Experience in java, angular, react and GO development.
Experience intrading business especially in structure note, single block trade is a plus. 
Experience in CI/CD, Kubernetes is a plus.   
Teamwork, problem solving and good communication skills.
Ability to work under pressure and tight timelines. 
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

    #candidateJoin()
    #jobJoin()
    findJob("john.smith@email.com")

    return

main()
