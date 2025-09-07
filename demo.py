
from connectGraphDB import connectGraph
from connect_model import MODEL_RAG


model = MODEL_RAG
driver = connectGraph()

def search_skill(skill_input):
    embedding = model.encode([skill_input.lower()])[0].tolist()  # vector

    with driver.session() as session:

        # 2. Semantic vector search
        semantic_query = """
        CALL db.index.vector.queryNodes('skill_embedding_cos', $top_k, $embedding)
        YIELD node, score
        RETURN node.name AS name, score
        ORDER BY score DESC
        """
        semantic_result = session.run(semantic_query, {"top_k": 1, "embedding": embedding}).data()
        return [(r["name"], r["score"]) for r in semantic_result]

# ----------------------------
# Demo loop
# ----------------------------
if __name__ == "__main__":
    print("🔹 Job/Skill Semantic Search Demo")
    print("Type 'q' to quit.\n")

    while True:
        user_input = input("Enter skill/job: ").strip()
        if user_input.lower() == "q":
            break
        results = search_skill(user_input)

        if not results:
            print("No match found.\n")
        else:
            print("Top results:")
            for r in results:
                if isinstance(r, tuple):
                    print(f"- {r[0]} (score: {r[1]:.4f})")
                else:
                    print(f"- {r}")
            print()