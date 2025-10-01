from connect.connectGraphDB import connectGraph
from connect.connect_model import MODEL_RAG

model = MODEL_RAG

def search_skills(skill,session):

    #match name
    record = session.run("""
            MATCH (s:Skill)
            WHERE s.name = $skill
            RETURN s.name AS name
            LIMIT 1
        """, skill=skill).single()

    if record:
        return record["name"]
    
    #match find text
    result = session.run("""
        CALL db.index.fulltext.queryNodes("skillIndex", $q)
        YIELD node, score
        RETURN node.name, score
        ORDER BY score DESC
        LIMIT 1;
        """, q=skill)
    
    record = result.single()
    if record:
        best_match_name = record["node.name"]
        best_match_score = record["score"]
        if best_match_score > 1.5:
            return best_match_name+"1"

    #match llm
    query_emb = model.encode([skill.lower()])[0].tolist()
    result = session.run("""
        CALL db.index.vector.queryNodes('skill_embedding_cos', $top_k, $embedding)
        YIELD node, score
        RETURN node.name AS name, score
        """, top_k=1, embedding=query_emb)
    result = list(result)
    if float(result[0]["score"])>=0.8:
        return result[0]["name"]+"{}".format(float(result[0]["score"]))

    return ""

driver = connectGraph()
with driver.session() as session:
    while(True):
        skill = input()
        s = search_skills(skill,session)
        print(s)