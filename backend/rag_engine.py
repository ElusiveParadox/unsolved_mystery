import os
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

EVIDENCE_FOLDER = "../evidence"
INDEX_FOLDER = "../faiss_index"

embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

db = None


def read_file(path: str) -> str:
    if path.endswith(".pdf"):
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_index():
    global db
    texts, metas = [], []

    os.makedirs(EVIDENCE_FOLDER, exist_ok=True)

    for fname in os.listdir(EVIDENCE_FOLDER):
        if not (fname.endswith(".txt") or fname.endswith(".pdf")):
            continue

        path = os.path.join(EVIDENCE_FOLDER, fname)
        content = read_file(path)

        if content.strip():
            texts.append(content)
            metas.append({"source": fname})

    if not texts:
        db = None
        return

    db = FAISS.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metas
    )

    db.save_local(INDEX_FOLDER)


def load_index():
    global db
    if os.path.exists(INDEX_FOLDER):
        db = FAISS.load_local(
            INDEX_FOLDER,
            embedding_model,
            allow_dangerous_deserialization=True
        )


def query_rag(question: str):
    global db

    if db is None:
        load_index()

    if db is None:
        build_index()

    if db is None:
        return "No evidence uploaded yet.", [], []

    retrieved = db.similarity_search(question, k=3)

    context = ""
    chunks = []

    for r in retrieved:
        src = r.metadata["source"]
        txt = r.page_content

        context += f"Evidence from {src}:\n{txt}\n\n"
        chunks.append({"content": txt, "source": src})

    prompt = f"""
You are a Cold Case Detective AI.
Answer ONLY using evidence below.

{context}

Question: {question}

Rules:
- Always cite sources like: According to [source]...
- If missing, say so clearly.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content
    citations = list({c["source"] for c in chunks})

    return answer, citations, chunks
