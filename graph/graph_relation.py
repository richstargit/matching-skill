
from connect.connectGraphDB import connectGraph
from connect.connect_model import MODEL_RAG

from relation.skill_child import tech_child
from relation.skill_relate import tech_relate

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

def buildgraph():
    with driver.session() as session:
        # เพิ่ม skill nodes
        for skill in tech_child.keys():
            embedding = model.encode([skill.lower()])[0].tolist()
            session.write_transaction(add_skill, skill, embedding)

        for skill in tech_relate.keys():
            embedding = model.encode([skill.lower()])[0].tolist()
            session.write_transaction(add_skill, skill, embedding)

        # เพิ่ม relations skill->skill
        for skill, related_skills in tech_child.items():
            for related in related_skills:
                session.write_transaction(add_relation_skilltoskill, skill, related)

        for skill, related_skills in tech_relate.items():
            for related in related_skills:
                session.write_transaction(add_relation_skilltoskill, skill, related)
                
    driver.close()
    print("All skills")
    return

def main():
    buildgraph()
    return

main()