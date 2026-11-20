import os
import sys
import zlib

script_dir = os.path.dirname(os.path.abspath(__file__))
project_progress_dir = os.path.abspath(os.path.join(script_dir, ".."))
root_dir = os.path.abspath(os.path.join(project_progress_dir, ".."))

for path in [project_progress_dir, root_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

from part_1.preprocess import preprocess_line, get_json_data, get_csv_data
import part_2.inverted_index as tf_idf
import part_2.evaluation as eval
import part_3.ranking_bm25 as bm25
import numpy as np
from gensim.models import Word2Vec


#word2vec settings, kept in one place so the report can quote them
W2V_PARAMS = {
    'vector_size': 100,  #dimensions of every word vector
    'window': 5,         #words on each side that count as context
    'min_count': 1,      #keep every term, so no query term of a matching document is lost
    'sg': 1,             #skip-gram: better than CBOW for rare words such as brand names
    'epochs': 20,        #passes over the corpus; product texts are short, so more passes help
    'seed': 42,
    'workers': 1,        #one thread, so the trained vectors are the same on every run
}


def stable_hash(text):
    """
    Deterministic hash for gensim's initial word vectors.
    Python's built-in hash() changes between runs, which would change the vectors and the ranking.
    """
    return zlib.crc32(text.encode('utf-8'))


def get_doc_terms(record):
    """
    Terms of one product, built exactly like the TF-IDF index text (Part 2):
    title + description + brand + sub_category + product_details values, already preprocessed.
    """
    product_text = ' '.join(value for key, value in (record.get('product_details', {})).items())
    full_text = f"{record.get('title', '')} {record.get('description', '')} {record.get('brand', '')} {record.get('sub_category', '')} {product_text}"
    return full_text.split()


def train_word2vec(document_index, params=W2V_PARAMS):
    """
    Trains word2vec on our own corpus: one 'sentence' per product.
    The tokens are stemmed like the index, so query terms map to the same vocabulary.
    """
    sentences = [terms for terms in (get_doc_terms(record) for record in document_index.values()) if terms]
    model = Word2Vec(sentences=sentences, hashfxn=stable_hash, **params)
    return model


def text_to_vector(terms, model):
    """
    One vector for a whole text: the average of the vectors of its words (the method given in the assignment).
    Words the model does not know are skipped. Returns None if no word is known.
    """
    vectors = [model.wv[term] for term in terms if term in model.wv]
    if not vectors:
        return None
    return np.mean(vectors, axis=0)


def build_doc_vectors(document_index, model):
    """
    Precomputes the averaged vector of every product, so a search only has to average the query.
    """
    doc_vectors = {}
    for prod_id, record in document_index.items():
        vector = text_to_vector(get_doc_terms(record), model)
        if vector is not None:
            doc_vectors[prod_id] = vector
    return doc_vectors


def cosine_similarity(a, b):
    """cos(a, b) = a.b / (|a| |b|), 0 if one of the vectors is all zeros."""
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / norm) if norm > 0 else 0.0


def rank_documents_word2vec(query_terms, docs, doc_vectors, model):
    """
    Ranks the candidate documents by cosine similarity between the query vector and each document vector.
    Returns a list of (doc_id, score), best first.
    """
    query_vector = text_to_vector(query_terms, model)
    if query_vector is None:
        return []

    doc_scores = []
    for doc_id in docs:
        if doc_id in doc_vectors:
            doc_scores.append((doc_id, cosine_similarity(query_vector, doc_vectors[doc_id])))

    #ties are broken by doc_id so the order is the same on every run
    doc_scores.sort(key=lambda x: (-x[1], x[0]))
    return doc_scores


def search_word2vec_with_scores(query, index, document_index, model, doc_vectors):
    """
    Same conjunctive (AND) retrieval as TF-IDF and BM25, then word2vec + cosine ranking.
    Returns a list of (doc_id, score).
    """
    cleaned_query = preprocess_line(query)
    if not cleaned_query:
        return []

    query_terms = cleaned_query.split()

    #conjunctive search (AND)
    docs = None
    for term in query_terms:
        if term not in index:
            return []
        term_docs = {posting[0] for posting in index[term]}
        docs = term_docs if docs is None else docs.intersection(term_docs)
        if not docs:
            return []

    return rank_documents_word2vec(query_terms, docs, doc_vectors, model)


def search_word2vec(query, index, document_index, model, doc_vectors):
    """
    Retrieves matching documents for the query terms and ranks them by word2vec + cosine similarity.
    Returns only the ranked doc ids, like search_tf_idf and search_bm25, so it plugs into the same evaluation.
    """
    return [doc_id for doc_id, score in search_word2vec_with_scores(query, index, document_index, model, doc_vectors)]


def evaluate_on_labels(queries_map, val_df, algorithms, k=10):
    """
    Computes the Part 2 metrics for each algorithm on a validation file with 0/1 labels.
    algorithms: list of (name, search_function, extra_args).
    """
    rows = []
    for name, search_function, search_args in algorithms:
        totals = {'P': 0.0, 'R': 0.0, 'F1': 0.0, 'AP': 0.0, 'RR': 0.0, 'NDCG': 0.0}
        num_queries = 0
        for query_id, group in val_df.groupby('query_id'):
            if query_id not in queries_map:
                continue
            relevant_docs = group[group['labels'] == 1]['pid'].tolist()
            if not relevant_docs:
                continue
            retrieved_docs = search_function(queries_map[query_id], *search_args)
            p_at_k = eval.calculate_precision_at_k(retrieved_docs, relevant_docs, k)
            r_at_k = eval.calculate_recall_at_k(retrieved_docs, relevant_docs, k)
            totals['P'] += p_at_k
            totals['R'] += r_at_k
            totals['F1'] += eval.calculate_f1_score_at_k(p_at_k, r_at_k)
            totals['AP'] += eval.calculate_average_precision_at_k(retrieved_docs, relevant_docs, k)
            totals['RR'] += eval.calculate_reciprocal_rank(retrieved_docs, relevant_docs)
            totals['NDCG'] += eval.calculate_ndcg_at_k(retrieved_docs, relevant_docs, k)
            num_queries += 1
        if num_queries:
            rows.append({'Algorithm': name, f'P@{k}': totals['P'] / num_queries, f'R@{k}': totals['R'] / num_queries,
                         f'F1@{k}': totals['F1'] / num_queries, 'MAP': totals['AP'] / num_queries,
                         'MRR': totals['RR'] / num_queries, f'NDCG@{k}': totals['NDCG'] / num_queries})
    return rows


def main():
    dataset_file = os.path.join(root_dir, "data", "fashion_products_dataset.json")
    validation_file = os.path.join(root_dir, "data", "validation_labels.csv")
    TOP_K = 20

    print(f"Loading dataset from {dataset_file}...")
    dataset = get_json_data(dataset_file)
    if dataset is None:
        sys.exit(1)

    print("Building the inverted index (used for the AND retrieval)...")
    index, tf, df, idf, document_index = tf_idf.create_index_tfidf(dataset)
    print(f"Index built for {len(document_index)} documents.")

    print(f"Training word2vec on our corpus {W2V_PARAMS}...")
    model = train_word2vec(document_index)
    doc_vectors = build_doc_vectors(document_index, model)
    print(f"Vocabulary: {len(model.wv)} terms. Document vectors: {len(doc_vectors)}.\n")

    #the 5 queries we defined in Part 2
    test_queries = [
        "women tshirt round neck cotton",
        "ecko unl printed sweatshirt",
        "men solid blue track pants",
        "satin necktie set pocket square cufflinks",
        "checkered full sleeve party blazer"
    ]

    print("================ TOP-20 WITH WORD2VEC + COSINE ================")
    for query in test_queries:
        results = search_word2vec_with_scores(query, index, document_index, model, doc_vectors)
        print(f"\nQuery: '{query}' (Total Matches: {len(results)})")
        for rank, (pid, score) in enumerate(results[:TOP_K], start=1):
            title = document_index[pid].get('title', 'No Title')
            print(f" {rank:2d}. [{pid}] {title} (cosine: {score:.4f})")

        #how different is the word2vec order from TF-IDF and BM25 on the same matching documents?
        top_w2v = {pid for pid, score in results[:TOP_K]}
        top_tfidf = set(tf_idf.search_tf_idf(query, index, idf, tf, document_index)[:TOP_K])
        top_bm25 = set(bm25.search_bm25(query, index, document_index)[:TOP_K])
        print(f" >> Overlap of the top {TOP_K}: word2vec vs TF-IDF {len(top_w2v & top_tfidf)}, word2vec vs BM25 {len(top_w2v & top_bm25)}")

    #evaluation on the course's validation labels (they have relevant and non-relevant documents)
    val_df = get_csv_data(validation_file)
    if val_df is not None:
        queries_map = {1: "women full sleeve sweatshirt cotton", 2: "men slim jeans blue"}
        algorithms = [
            ("TF-IDF", tf_idf.search_tf_idf, (index, idf, tf, document_index)),
            ("BM25", bm25.search_bm25, (index, document_index)),
            ("word2vec + cosine", search_word2vec, (index, document_index, model, doc_vectors)),
        ]
        import pandas as pd
        for k in (10, 20):
            print(f"\n================ EVALUATION ON validation_labels.csv (K={k}) ================")
            print(pd.DataFrame(evaluate_on_labels(queries_map, val_df, algorithms, k=k)).set_index('Algorithm').round(3))

    #evaluation on the team's master labels (the pooled top 20 of TF-IDF, BM25 and Custom for our 5 queries)
    #word2vec was not part of that pool, so a product it finds outside the pool counts as not relevant
    master_file = os.path.join(project_progress_dir, "part_3", "validation_labels_master.csv")
    master_df = get_csv_data(master_file)
    if master_df is not None:
        import pandas as pd
        import part_3.custom_ranking as custom
        field_weights = {'title': 4.0, 'brand': 3.0, 'sub_category': 2.0, 'description': 1.0, 'product_details': 1.0}
        index_c, tf_c, df_c, idf_c, document_index_c = custom.create_index_tfidf_custom(dataset, field_weights)
        queries_map = {i + 1: query for i, query in enumerate(test_queries)}
        algorithms = [
            ("TF-IDF", tf_idf.search_tf_idf, (index, idf, tf, document_index)),
            ("BM25", bm25.search_bm25, (index, document_index)),
            ("Custom", custom.search_tf_idf_custom, (index_c, idf_c, tf_c, document_index_c)),
            ("word2vec + cosine", search_word2vec, (index, document_index, model, doc_vectors)),
        ]
        print(f"\n================ EVALUATION ON validation_labels_master.csv (K={TOP_K}) ================")
        print(pd.DataFrame(evaluate_on_labels(queries_map, master_df, algorithms, k=TOP_K)).set_index('Algorithm').round(3))


if __name__ == "__main__":
    main()
