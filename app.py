import json
from init import addJob, addUser, extractData, extractJob, find_Job, readPDF

def candidateJoin():
    readData = readPDF("dataset/resume/Thomas_Nguyen_Investment_Banking_Analyst_en_minimal.pdf")
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
    


def main():

    #candidateJoin()
    #jobJoin()
    findJob("Ahmed Rashid")

    return

main()
