import json
from connect.connectGraphDB import connectGraph
from connect.connect_model import MODEL_RAG
from relation.match_skill_data import skills_data

driver = connectGraph()

model = MODEL_RAG

def add_skill(tx, skill_name, embedding):
    tx.run("""
        MERGE (s:Skill {name: $name})
        SET s.embedding = $embedding
    """, name=skill_name, embedding=embedding)

def add_relation_skilltoskill(tx, skill_name, related_skill):
    tx.run("""
        MATCH (s1:Skill {name: $skill_name})
        MATCH (s2:Skill {name: $related_skill})
        MERGE (s1)-[:HAS_SKILL]->(s2)
    """, skill_name=skill_name, related_skill=related_skill)

def add_exp(tx, exp_name, embedding):
    tx.run("""
        MERGE (s:Experience {name: $name})
        SET s.embedding = $embedding
    """, name=exp_name, embedding=embedding)

def add_relation_exptoskill(tx, exp_name, related_skill):
    tx.run("""
        MATCH (e1:Experience {name: $exp_name})
        MATCH (s1:Skill {name: $related_skill})
        MERGE (e1)-[:HAS_SKILL]->(s1)
    """, exp_name=exp_name, related_skill=related_skill)

def create_vector_index():
    with driver.session() as session:
        session.run("""
        CREATE VECTOR INDEX skill_embedding_cos
        FOR (s:Skill)
        ON (s.embedding)
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: 768,
            `vector.similarity_function`: 'cosine'
          }
        }
        """)
    print("✅ Vector Index Created")

def create_name_index():
    with driver.session() as session:
        session.run("""
        CREATE FULLTEXT INDEX skill_name_index
        FOR (s:Skill)
        ON EACH [s.name]
        """)
    print("✅ Name Index Created")

def build_graph():
    with driver.session() as session:
        # เพิ่ม skill nodes
        for skill in skills_data.keys():
            embedding = model.encode([skill])[0].tolist()  # แปลงเป็น list เพื่อเก็บใน Neo4j
            session.write_transaction(add_skill, skill, embedding)

        # เพิ่ม relations skill->skill
        for skill, related_skills in skills_data.items():
            for related in related_skills:
                session.write_transaction(add_relation_skilltoskill, skill, related)

        exps_data = get_exp()
        #เพิ่ม node exp
        for exp in exps_data.keys():
            embedding = model.encode([exp])[0].tolist()
            session.write_transaction(add_exp,exp,embedding)
        #เพิ่ม relation exp->skill
        for exp,related in exps_data.items():
            for r in related:
                session.write_transaction(add_relation_exptoskill,exp,r)
                
    driver.close()
    print("All skills and relations added to Neo4j Aura.")

def get_skill():
    # Paths
    json_path = "dataset/resume_all_extended.json"

    # Load
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    skillset = set()
    for d in data:
        skillset.update(d['skills'])
        for e in d['experiencesList']:
            skillset.update(e['technologies'])
    
    return skillset

def get_exp():
    # Paths
    json_path = "dataset/resume_all_extended.json"

    # Load
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expset = {}
    for d in data:
        for e in d['experiencesList']:
            key = e['positionName']
            techs = e['technologies']

            if key in expset:
                # รวม list เดิมกับ list ใหม่ (ไม่ซ้ำกันก็ได้)
                expset[key].extend(techs)
            else:
                expset[key] = list(techs)
    
    return expset

def save_exp():
    exps = get_exp()
    with open("exp.txt", "w", encoding="utf-8") as f:
        for d in exps:
            f.write(d + "\n")   # เขียนทีละบรรทัด
    print("✅ Saved to exps.txt")

def save_skill():
    skills = get_skill()
    with open("skills.txt", "w", encoding="utf-8") as f:
        for d in skills:
            f.write(d + "\n")   # เขียนทีละบรรทัด
    print("✅ Saved to skills.txt")

def main():
    #save_skill()
    #build_graph()
    try:
        create_vector_index()
    except Exception as e:
        e

main()