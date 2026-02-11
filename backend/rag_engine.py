import os
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

EVIDENCE_FOLDER = "../evidence"

vectorizer = None
doc_texts = []
doc_sources = []
doc_vectors = None


def read_file(path: str) -> str:
    if path.endswith(".pdf"):
        reader = PdfReader(path)
        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_index():
    global vectorizer, doc_texts, doc_sources, doc_vectors

    doc_texts = []
    doc_sources = []

    os.makedirs(EVIDENCE_FOLDER, exist_ok=True)

    for fname in os.listdir(EVIDENCE_FOLDER):
        if not fname.endswith((".txt", ".pdf")):
            continue

        path = os.path.join(EVIDENCE_FOLDER, fname)
        content = read_file(path)

        if content.strip():
            doc_texts.append(content)
            doc_sources.append(fname)

    if not doc_texts:
        doc_vectors = None
        return

    vectorizer = TfidfVectorizer(stop_words="english")
    doc_vectors = vectorizer.fit_transform(doc_texts)


def query_rag(question: str):
    global doc_vectors

    if doc_vectors is None:
        build_index()

    if doc_vectors is None:
        return "No evidence uploaded yet.", [], []

    q_vector = vectorizer.transform([question])
    sims = cosine_similarity(q_vector, doc_vectors)[0]

    top_indices = sims.argsort()[-3:][::-1]

    context = ""
    chunks = []

    for idx in top_indices:
        src = doc_sources[idx]
        txt = doc_texts[idx][:1500]

        context += f"Evidence from {src}:\n{txt}\n\n"
        chunks.append({"content": txt, "source": src})

    prompt = f"""
You are a Cold Case Detective AI.
Answer ONLY using evidence below.

{context}

Question: {question}

Rules:
- Always cite sources like: According to [filename]...
- If evidence is missing, say so clearly.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content
    citations = list({c["source"] for c in chunks})

    return answer, citations, chunks
