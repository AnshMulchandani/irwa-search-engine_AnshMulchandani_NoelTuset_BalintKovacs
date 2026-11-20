"""
Exercise 3 experiment: compares text representations on data/validation_labels.csv,
with the same AND retrieval: word2vec average, IDF-weighted word2vec average, Doc2Vec (PV-DBOW).
Run from project_progress: python -m part_3.representation_experiments
"""
import os, sys, numpy as np
PP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if PP not in sys.path:
    sys.path.insert(0, PP)
from part_1.preprocess import get_json_data, get_csv_data, preprocess_line
import part_2.inverted_index as tf_idf
import part_3.word2vec_ranking as w2v
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import pandas as pd

ROOT = os.path.dirname(PP)
data = get_json_data(os.path.join(ROOT, "data", "fashion_products_dataset.json"))
index, tf, df, idf, document_index = tf_idf.create_index_tfidf(data)
model = w2v.train_word2vec(document_index)
plain = w2v.build_doc_vectors(document_index, model)

def weighted_vector(terms):
    vecs, ws = [], []
    for t in terms:
        if t in model.wv:
            vecs.append(model.wv[t]); ws.append(idf.get(t, 0.0))
    if not vecs or sum(ws) == 0: return None
    return np.average(vecs, axis=0, weights=ws)
weighted = {pid: v for pid, v in ((pid, weighted_vector(w2v.get_doc_terms(r))) for pid, r in document_index.items()) if v is not None}

tagged = [TaggedDocument(w2v.get_doc_terms(r), [pid]) for pid, r in document_index.items() if w2v.get_doc_terms(r)]
d2v = Doc2Vec(tagged, vector_size=100, window=5, min_count=1, epochs=20, dm=0, dbow_words=1, seed=42, workers=1, hashfxn=w2v.stable_hash)

def and_docs(q):
    terms = preprocess_line(q).split(); docs = None
    for t in terms:
        if t not in index: return terms, set()
        s = {p[0] for p in index[t]}; docs = s if docs is None else docs & s
    return terms, docs or set()

def make_search(kind):
    def search(q, *_):
        terms, docs = and_docs(q)
        if kind == "weighted":
            qv = weighted_vector(terms); vecs = weighted
        else:
            d2v.random.seed(42); qv = d2v.infer_vector(terms, epochs=100); vecs = {p: d2v.dv[p] for p in docs}
        if qv is None: return []
        sc = [(p, w2v.cosine_similarity(qv, vecs[p])) for p in docs if p in vecs]
        sc.sort(key=lambda x: (-x[1], x[0])); return [p for p, s in sc]
    return search

if __name__ != "__main__":
    raise SystemExit("run as a script: python -m part_3.representation_experiments")
val = get_csv_data(os.path.join(ROOT, "data", "validation_labels.csv"))
qmap = {1: "women full sleeve sweatshirt cotton", 2: "men slim jeans blue"}
algos = [("TF-IDF", tf_idf.search_tf_idf, (index, idf, tf, document_index)),
         ("word2vec average", w2v.search_word2vec, (index, document_index, model, plain)),
         ("word2vec IDF-weighted", make_search("weighted"), ()),
         ("Doc2Vec (PV-DBOW)", make_search("d2v"), ())]
for k in (10, 20):
    print(f"--- K={k}"); print(pd.DataFrame(w2v.evaluate_on_labels(qmap, val, algos, k=k)).set_index("Algorithm").round(3))
