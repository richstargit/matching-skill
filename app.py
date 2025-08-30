import json
from init import addUser, extractData, readPDF

def main():

    readData = readPDF("dataset/resume/Ahmed_Rashid_Senior_Backend_Engineer_en_modern.pdf")
    if not readData['success']:
        return
    
    res = extractData(readData['data']).strip("`").replace("json", "", 1).strip()
    data = json.loads(res)
    addUser(data)
    

    return

main()
