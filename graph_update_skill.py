import json
import os
import time
from connectGraphDB import connectGraph
from connect_model import MODEL_RAG
from graph import add_exp, add_relation_exptoskill, add_relation_skilltoskill, add_skill, get_exp
from init import extractJob

from skill_relation import DATA_SKILL

driver = connectGraph()

model = MODEL_RAG

def extract_skill(title,des):
    readData = '''
        job:{}
        description:{}
    '''.format(title,des)
    res = extractJob(readData).strip("`").replace("json", "", 1).strip()
    data = json.loads(res)
    with open("dataset/update_skill/{}.txt".format(title), "a", encoding="utf-8") as f:
        with open("dataset/update_skill/{}_relate.txt".format(title), "a", encoding="utf-8") as rf:
            for d in data['skills']:
                with driver.session() as session:
                    query_emb = model.encode([d.lower()])[0].tolist()
                    result = session.run("""
                        CALL db.index.vector.queryNodes('skill_embedding_cos', $top_k, $embedding)
                        YIELD node, score
                        RETURN node.name AS name, score
                    """, top_k=1, embedding=query_emb)
                    result = list(result)
                if float(result[0]["score"])>=0.9:
                    print("{} <-{}-> {}".format(d,result[0]["score"],result[0]["name"]))
                    rf.write("{} <-> {}".format(d,result[0]["name"])+"\n")
                    continue
                print("add:",d)
                f.write(d + "\n")   # เขียนทีละบรรทัด
    print("✅ Saved to {}.txt".format(title))

def clean_data():
    for filename in os.listdir("dataset/update_skill/extract"):
        file_path = os.path.join("dataset/update_skill/extract", filename)
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        data = set(lines)
        with open("dataset/update_skill/clean/{}".format(filename), "w", encoding="utf-8") as f:
            for skill in sorted(data):  # sorted เพื่อเรียงลำดับ
                f.write(skill + "\n")

    return

def update_skill():
    with driver.session() as session:
        # เพิ่ม skill nodes
        for job in DATA_SKILL:
            for skill in job.keys():
                embedding = model.encode([skill.lower()])[0].tolist()  # แปลงเป็น list เพื่อเก็บใน Neo4j
                session.write_transaction(add_skill, skill, embedding)

            # เพิ่ม relations skill->skill
            for skill, related_skills in job.items():
                for related in related_skills:
                    session.write_transaction(add_relation_skilltoskill, skill, related)

        exps_data = get_exp()
        #เพิ่ม node exp
        for exp in exps_data.keys():
            embedding = model.encode([exp.lower()])[0].tolist()
            session.write_transaction(add_exp,exp,embedding)
        #เพิ่ม relation exp->skill
        for exp,related in exps_data.items():
            for r in related:
                session.write_transaction(add_relation_exptoskill,exp,r)
                
    driver.close()
    print("All skills")
    return


def main():
    # df = pd.read_csv('dataset/jobs_data.csv')
    # for i in range(715,len(df)):
    #     extract_skill(df.iloc[i]['job_type'],df.iloc[i]['des'])
    #     time.sleep(1)
    #clean_data()
    update_skill()

main()