
from connect.connectGraphDB import connectGraph
from connect.connect_model import MODEL_RAG

from relation.skill_child import tech_skills_child
from relation.skill_relate import tech_skills_relate

driver = connectGraph()

model = MODEL_RAG

def add_skill(tx, skill_name, embedding):
    tx.run("""
        MERGE (s:Skill {name: $name})
        SET s.embedding = $embedding
    """, name=skill_name, embedding=embedding)

def add_relate_skilltoskill(tx, skill_name, related_skill):
    tx.run("""
        MATCH (s1:Skill {name: $skill_name})
        MATCH (s2:Skill {name: $related_skill})
        MERGE (s1)-[:RELATE]->(s2)
        MERGE (s2)-[:RELATE]->(s1)
    """, skill_name=skill_name, related_skill=related_skill)

def add_child_skilltoskill(tx, child_skill, core_skill):
    tx.run("""
        MATCH (s1:Skill {name: $core_skill})
        MATCH (s2:Skill {name: $child_skill})
        MERGE (s2)-[:CHILD]->(s1)
    """, core_skill=core_skill, child_skill=child_skill)

def create_vector_index_skill():
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

def create_vector_index_exp():
    with driver.session() as session:
        session.run("""
        CREATE VECTOR INDEX experience_embedding_cos
        FOR (s:Experience)
        ON (s.embedding)
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: 768,
            `vector.similarity_function`: 'cosine'
          }
        }
        """)
    print("✅ Vector Index Created")

def create_vector_index_edu():
    with driver.session() as session:
        session.run("""
        CREATE VECTOR INDEX education_embedding_cos
        FOR (s:Education)
        ON (s.embedding)
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: 768,
            `vector.similarity_function`: 'cosine'
          }
        }
        """)
    print("✅ Vector Index Created")

def buildgraph():
    with driver.session() as session:
        # เพิ่ม skill nodes
        for skill in tech_skills_child.keys():
            embedding = model.encode([skill.lower()])[0].tolist()
            session.write_transaction(add_skill, skill.lower(), embedding)

        for skill in tech_skills_relate.keys():
            embedding = model.encode([skill.lower()])[0].tolist()
            session.write_transaction(add_skill, skill.lower(), embedding)

        # เพิ่ม relations skill->skill
        for skill, related_skills in tech_skills_relate.items():
            for related in related_skills:
                embedding = model.encode([related.lower()])[0].tolist()
                session.write_transaction(add_skill, related.lower(), embedding)
                session.write_transaction(add_relate_skilltoskill, skill.lower(), related.lower())

        for skill, core_skills in tech_skills_child.items():
            for core in core_skills:
                embedding = model.encode([core.lower()])[0].tolist()
                session.write_transaction(add_skill, core.lower(), embedding)
                session.write_transaction(add_child_skilltoskill, skill.lower(), core.lower())
                
    driver.close()
    print("All skills")
    return

def main():
    buildgraph()
    #create_vector_index_skill()
    #create_vector_index_exp()
    #create_vector_index_edu()

    return

main()