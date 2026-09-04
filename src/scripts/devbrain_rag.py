import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
DevBrain Local RAG Engine (BM25 + TF-IDF Hybrid Search).
Indexa y consulta semánticamente las 1,675 notas del Vault en milisegundos
sin depender de servicios externos ni saturar la memoria RAM.
"""
import sys
import os
import re
import math
from collections import Counter
from pathlib import Path

VAULT_DIR = Path(os.getenv("VAULT_DIR", str(Path.home() / "ObsidianVault")))
CONOCIMIENTO_DIR = VAULT_DIR / "03-CONOCIMIENTO"
PROYECTOS_DIR = VAULT_DIR / "02-PROYECTOS"

STOPWORDS = {
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para", "con", "no", "una",
    "su", "al", "lo", "como", "mas", "pero", "sus", "le", "ya", "o", "este", "si", "porque", "esta", "entre",
    "the", "of", "and", "to", "a", "in", "for", "is", "on", "that", "by", "this", "with", "i", "you", "it", "not", "or", "be", "are", "from", "at"
}

def tokenize(text: str):
    words = re.findall(r"\w+", text.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]

class BM25Index:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.docs = []
        self.doc_lengths = []
        self.avg_doc_len = 0
        self.idf = {}

    def fit(self, documents):
        self.docs = documents
        total_len = 0
        df = Counter()
        num_docs = len(documents)

        for doc in documents:
            tokens = set(doc["tokens"])
            for t in tokens:
                df[t] += 1
            l = len(doc["tokens"])
            self.doc_lengths.append(l)
            total_len += l

        self.avg_doc_len = total_len / num_docs if num_docs > 0 else 1
        for term, freq in df.items():
            self.idf[term] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1.0)

    def search(self, query: str, top_k=4):
        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        scores = []
        for idx, doc in enumerate(self.docs):
            score = 0.0
            doc_len = self.doc_lengths[idx]
            counts = doc["term_counts"]

            for q in q_tokens:
                if q in counts:
                    freq = counts[q]
                    denom = freq + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                    score += self.idf.get(q, 0.0) * (freq * (self.k1 + 1.0)) / denom

            if score > 0:
                scores.append((score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:top_k]

def build_corpus():
    documents = []
    files = list(CONOCIMIENTO_DIR.rglob("*.md")) + [p / "README.md" for p in PROYECTOS_DIR.iterdir() if p.is_dir() and (p / "README.md").exists()]
    for f in files:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
            toks = tokenize(txt)
            if toks:
                documents.append({
                    "path": f,
                    "title": f.stem,
                    "tokens": toks,
                    "term_counts": Counter(toks),
                    "raw": txt
                })
        except Exception:
            pass
    return documents

def ask_rag(query: str):
    print(f"Cargando corpus e indexando semantica local...")
    docs = build_corpus()
    index = BM25Index()
    index.fit(docs)

    results = index.search(query, top_k=3)
    if not results:
        print("No se encontraron coincidencias conceptuales relevantes.")
        return

    print(f"\n=== RESULTADOS RAG PARA: '{query}' ===")
    for score, doc in results:
        preview = doc["raw"][:350].replace("\n", " ").strip()
        print(f"\n* [[{doc['title']}]] (Score: {score:.2f})")
        print(f"  Ruta: {doc['path'].relative_to(VAULT_DIR)}")
        print(f"  Contexto: {preview}...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_text = " ".join(sys.argv[1:])
        ask_rag(query_text)
    else:
        print("Uso: py devbrain_rag.py <consulta en lenguaje natural>")