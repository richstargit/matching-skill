from init import extractData, readPDF

def main():

    readData = readPDF("dataset/resume/Elena_Popov_AI_Engineering_Manager_en_classic.pdf")
    if not readData['success']:
        return
    
    res = extractData(readData['data'])

    print(res)

    return

main()
