import random
import numpy as np
import os
from gensim.models import Word2Vec
    
from myapp.search.objects import Document
from project_progress.part_1.preprocess import get_json_data
import project_progress.part_2.inverted_index as tf_idf
import project_progress.part_3.ranking_bm25 as bm25
import project_progress.part_3.custom_ranking as custom
import project_progress.part_3.word2vec_ranking as w2v

def dummy_search(corpus: dict, search_id, num_results=20):
    """
    Just a demo method, that returns random <num_results> documents from the corpus
    :param corpus: the documents corpus
    :param search_id: the search id
    :param num_results: number of documents to return
    :return: a list of random documents from the corpus
    """
    res = []
    doc_ids = list(corpus.keys())
    docs_to_return = np.random.choice(doc_ids, size=num_results, replace=False)
    for doc_id in docs_to_return:
        doc = corpus[doc_id]
        res.append(Document(pid=doc.pid, title=doc.title, description=doc.description,
                            url="doc_details?pid={}&search_id={}&param2=2".format(doc.pid, search_id), ranking=random.random()))
    return res

class SearchEngine:
    """Class that implements the search engine logic"""

    """
    def search(self, search_search_query, search_id, corpus):
        print("Search search_query:", search_search_query)

        results = []
        ### You should implement your search logic here:
        results = dummy_search(corpus, search_id)  # replace with call to search algorithm

        # results = search_in_corpus(search_search_query)
        return results
    """
    #helper
    @staticmethod
    def _format_product_details(details):
        """Flattens [{'Fabric': 'Cotton Blend'}, ...] into {'Fabric': 'Cotton Blend', ...} for display without steaming"""
        if isinstance(details, dict):
            return details
        flat = {}
        for entry in details or []:
            if isinstance(entry, dict):
                for key, value in entry.items():
                    flat[key] = f"{flat[key]}, {value}" if key in flat else value
        return flat
    
    
    def __init__(self, dataset_path: str = "data/fashion_products_dataset.json"):
        #initial weights for custom search
        self.field_weights = {
            "title": 4.0,
            "brand": 3.0,
            "sub_category": 2.0,
            "description": 1.0,
            "product_details": 1.0,
        }

        print(f"Loading raw dataset from {dataset_path}...")
        dataset = get_json_data(dataset_path)
        if not dataset:
            raise FileNotFoundError(f"Dataset could not be loaded from {dataset_path}")

        # Preserve original un-stemmed fields for UI rendering
        self.raw_corpus = {
            item["pid"]: item for item in dataset if "pid" in item
        }

        # Build standard index (TF-IDF & BM25) once at startup
        print("Building Standard Inverted Index...")
        self.index, self.tf, self.df, self.idf, self.document_index = (
            tf_idf.create_index_tfidf(dataset)
        )

        # Computes document length in cache for BM25
        bm25.get_doc_lengths(self.index, len(self.document_index))

        # Build custom weighted index once at startup
        print("Building Custom Weighted Inverted Index...")
        (
            self.index_custom,
            self.tf_custom,
            self.df_custom,
            self.idf_custom,
            self.document_index_custom,
        ) = custom.create_index_tfidf_custom(dataset, self.field_weights)

        # Train or load Word2Vec model and precompute document vectors once at startup
        model_path = os.path.join(os.path.dirname(dataset_path), "word2vec.model")
        if os.path.exists(model_path):
            print(f"Loading cached Word2Vec model from {model_path}...")
            self.w2v_model = Word2Vec.load(model_path)
        else:
            print("Training Word2Vec model (first run only)...")
            self.w2v_model = w2v.train_word2vec(self.document_index)
            self.w2v_model.save(model_path)

        print("Building Word2Vec document vectors...")
        self.w2v_doc_vectors = w2v.build_doc_vectors(self.document_index, self.w2v_model)

        print(f"SearchEngine ready with {len(self.raw_corpus)} products.")

    def search(self, search_query, search_id, corpus, algorithm="custom", num_results=20):
        """
        It retrives the top_k documents based on the search_query and the ranking algoritm
        If there is no ranking algorithm specified it uses the custom ranking, it can be tunned
        """
        #if there is no search_query we return
        if not search_query or not search_query.strip():
            return []
        #The search applies one of the ranking algorithm depending on what is defined
        if algorithm == "tfidf":
            ranked_pids = tf_idf.search_tf_idf(
                search_query, self.index, self.idf, self.tf, self.document_index
            )
        elif algorithm == "bm25":
            ranked_pids = bm25.search_bm25(
                search_query, self.index, self.document_index
            )
        elif algorithm == "word2vec":
            ranked_pids = w2v.search_word2vec(
                search_query,
                self.index,
                self.document_index,
                self.w2v_model,
                self.w2v_doc_vectors,
            )
        else:
            ranked_pids = custom.search_tf_idf_custom(
                search_query,
                self.index_custom,
                self.idf_custom,
                self.tf_custom,
                self.document_index_custom,
            )

        results = []
        for rank, pid in enumerate(ranked_pids[:num_results], start=1):
            raw_doc = self.raw_corpus.get(pid, {})

            results.append(
                Document(
                    # --- Mandatory results-page fields ---
                    pid=pid,
                    title=raw_doc.get("title") or "Untitled Product",
                    description=raw_doc.get("description") or "No description available.",
                    selling_price=raw_doc.get("selling_price"),
                    discount=raw_doc.get("discount"),
                    average_rating=raw_doc.get("average_rating"),
                    url=raw_doc.get("url") or "#",
                    # --- Additional product fields ---
                    brand=raw_doc.get("brand") or "Unknown",
                    category=raw_doc.get("category") or "N/A",
                    sub_category=raw_doc.get("sub_category") or "N/A",
                    product_details=self._format_product_details(raw_doc.get("product_details")),
                    seller=raw_doc.get("seller") or "N/A",
                    out_of_stock=bool(raw_doc.get("out_of_stock", False)),
                    actual_price=raw_doc.get("actual_price"),
                    images=raw_doc.get("images") or [],
                    # --- Extra fields added to objects.py useful for analitics ---
                    ranking=rank,
                    doc_details_url=f"doc_details?pid={pid}&search_id={search_id}",
                )
            )

        return results