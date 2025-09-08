# augment/qgen_llm.py
import os, json, uuid, random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.pinecone_vectorstore import get_vectorstore
from src.helper import load_pdf_files, process_documents
from src.config import NAMESPACE, PINECONE_INDEX
print("[qgen] Using namespace:", NAMESPACE)
print("[qgen] Using index:", PINECONE_INDEX)

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Try several seed queries (increase coverage)
SEED_QUERIES = [
    "leave policy", "annual leave", "attendance", "overtime",
    "security policy", "onboarding", "probation", "termination",
    "user manual", "login", "payroll", "Gallery HR"
]

def make_questions_for_chunk(text: str, n: int = 5) -> list[str]:
    prompt = (
        "You are generating end-user questions for a company FAQ chatbot.\n"
        "Given the snippet below, produce {n} diverse, realistic questions.\n"
        "Do NOT copy sentences verbatim; vary phrasing and specificity.\n\n"
        f"SNIPPET:\n{text}\n\nReturn one question per line."
    ).replace("{n}", str(n))
    out = llm.invoke(prompt).content.strip().splitlines()
    # tidy bullets/numbers
    return [q.strip().lstrip("-•0123456789. )(").strip() for q in out if q.strip()]

def pick_seeds_from_vectorstore(k_total=12):
    vs = get_vectorstore()  # uses your .env namespace
    seeds = []
    for q in SEED_QUERIES:
        try:
            need = max(0, k_total - len(seeds))
            if need == 0:
                break
            seeds.extend(vs.similarity_search(q, k=min(4, need)))
        except Exception:
            # keep trying other seeds even if one fails
            pass
    return seeds[:k_total]

def pick_seeds_from_docs(k_total=12, docs_path="Docs/"):
    docs = load_pdf_files(docs_path)
    chunks = process_documents(docs)
    if not chunks:
        return []
    random.shuffle(chunks)
    return chunks[:k_total]

def main():
    # 1) Try vectorstore seeds first
    seeds = pick_seeds_from_vectorstore(k_total=12)

    # 2) Fallback to raw PDFs if vectorstore returned nothing
    if not seeds:
        print("[qgen] Vectorstore returned 0 seeds. Falling back to Docs/ …")
        seeds = pick_seeds_from_docs(k_total=12, docs_path="Docs/")

    if not seeds:
        print("[qgen] No seeds found (vectorstore and Docs/ empty). Exiting.")
        return

    out = []
    for d in seeds:
        qs = make_questions_for_chunk(d.page_content, n=5)
        for q in qs:
            out.append({
                "id": str(uuid.uuid4()),
                "question": q,
                "source": d.metadata.get("source"),
                "page": d.metadata.get("page"),
                "type": "llm_aug"
            })

    os.makedirs("data", exist_ok=True)
    with open("data/aug_questions.jsonl", "w", encoding="utf-8") as f:
        for row in out:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"[qgen] wrote {len(out)} questions to data/aug_questions.jsonl")

if __name__ == "__main__":
    main()
