# Part 2: Indexing and Evaluation

## Setup

From the repository root:

```
pip install -r requirements.txt

```
And also for this part install

```
python3 -m pip install gensim

```

Put the dataset at `data/fashion_products_dataset.json` and ensure the validation labels are in the corresponding place (bm25, custom and master in part3 and tf_idf in part2).
The NLTK stop word list downloads automatically on first run.

And activate the `irwa.venv`

## Files

| File | What it does |
|---|---|
| `custom_ranking.py` | Creates the inverted_index, (`create_index_tfidf`), search for documents that have all the terms in query and returns the documents ranked using TF-IDF.(`search_tf_idf`) the ranking part is done by (`rank_documents`)

| File | What it does |
|---|---|
| `ranking_bm25.py` | Loads the product dataset, builds the TF-IDF index, and executes search retrieval across the 5 predefined test queries. Outputs the matching product count and prints the top ranked retrieved items per query to evaluate ranking quality. |

| File | What it does |
|---|---|
| `test_retrival.py` | Evaluates the search engine's retrieval and ranking performance against ground truth data. Computes depth-specific metrics (`calculate_precision_at_k`, `calculate_recall_at_k`, `calculate_f1_score_at_k`, `calculate_ndcg_at_k`) and overall ranking quality metrics (`calculate_average_precision`, `calculate_reciprocal_rank`). The main function executes this calculation across all queries.


## Run

All commands from `project_progress`:

To evaluate custom ranking:
```python (or python3)
python -m part_3.custom_ranking
```

To compute all the comparison between ranking algorithms:
```python (or python3)
python -m part_3.test_retrival
```
To evaluate word2vec ranking:
```python (or python3)
python -m part_3.word2vec_ranking
```
To run the experiments:
```python (or python3)
python3 -m part_3.representation_experiments
```

## Function Reference (`custom_ranking.py`)

- **`calculate_custom_multiplier(record, a=1.0, b=2.0, c=0.8)`**: Calculates a business value multiplier for a product record by combining its discount percentage, logarithmic cash savings (`actual_price - selling_price`), and an availability penalty if the item is out of stock. Returns the final scalar multiplier.
- **`create_index_tfidf_custom(data, field_weights=None)`**: Builds the inverted index mapping terms to documents, positions, and field weights, while computing and storing each document's custom business multiplier. Calculates weighted normalized Term Frequency (TF), Document Frequency (DF), and Inverse Document Frequency (IDF). Returns the inverted index, TF lists, DF, IDF, and the preprocessed document index.
- **`rank_documents_tf_idf_custom(terms, docs, index, idf, tf, document_index)`**: Calculates the cosine similarity (dot product) between the query vector and candidate document vectors using their weighted TF-IDF scores, and multiplies the result by each document's precomputed business value multiplier. Returns a sorted list of document IDs from most to least relevant.
- **`search_tf_idf_custom(query, index, idf, tf, document_index)`**: Preprocesses the user's input query, filters for candidate documents that contain all terms in the query (Boolean AND search), and passes them to `rank_documents_tf_idf_custom` for scoring. Returns the final ranked list.

For `calculate_custom_multiplier`:
1. Extract `actual_price`, `selling_price`, and `discount` from the product record.
2. Compute the absolute cash saved (`actual_price - selling_price`) and calculate the `value_score` using the formula `(discount * a) + (log(money_saved + 1) * b)`.
3. Convert the score into a base multiplier (`1.0 + value_score / 100.0`), defaulting to `1.0` if price fields are missing or invalid.
4. Check the `out_of_stock` flag; if the product is out of stock, apply the stock penalty `c` (default `0.8`), otherwise keep it at `1.0`.
5. Multiply and return `multiplier * stock_penalty`.

For `create_index_tfidf_custom`:
1. Preprocess the entire dataset using `preprocess_doc` to retrieve a clean `document_index`.
2. Loop through every document in the index, compute its `value_multiplier` via `calculate_custom_multiplier`, and store it directly in the document's record.
3. Extract separate text fields (`title`, `brand`, `sub_category`, `description`, and `product_details` values) and iterate over each field's terms using its corresponding weight from `field_weights`.
4. Build a local `current_page_index` storing each term's document ID, positional indices, and array of field weights.
5. Calculate the document's L2 norm using the square root of the sum of squared weighted term counts (`sum(posting[2]) ** 2`).
6. For each term in the local index, calculate the normalized weighted TF (`weighted_count / norm`), increment the global Document Frequency (DF) counter, and append the posting to the global inverted index.
7. After processing all documents, compute the IDF for every unique term using the base-2 logarithm formula `log2(num_documents / df[term])`.

For `rank_documents_tf_idf_custom`:
1. Initialize a `query_vector` (list of zeros) and a `doc_vectors` dictionary (mapping each candidate document ID to a list of zeros), both sized to the number of terms in the query.
2. Count the frequency of each term in the query and compute the L2 norm of these counts to normalize the query length.
3. Iterate through each term in the query along with its index position, skipping terms not present in the global index.
4. Calculate the query's TF-IDF score (`(count / query_norm) * idf[term]`) and assign it to `query_vector[termIndex]`.
5. Loop through the inverted index postings for the current term; for each posting belonging to a candidate document, compute its weighted TF-IDF score (`tf[term][doc_index] * idf[term]`) and store it in `doc_vectors[doc][termIndex]`.
6. Calculate the final score for each candidate document by taking the dot product between its `doc_vector` and `query_vector`, then multiplying by the document's stored `value_multiplier`.
7. Sort the candidate documents by their final adjusted score in descending order and return the ordered list of document IDs.

For `search_tf_idf_custom`:
1. Clean the query string using `preprocess_line` and return an empty list if the result is empty.
2. Split the cleaned query into individual query terms.
3. Iterate through each term and perform a strict conjunctive search (Boolean AND) by taking the set intersection (`docs.intersection`) of all document IDs containing the current term.
4. Return an empty list immediately if any query term is absent from the index or if the intersection becomes empty.
5. Pass the candidate document IDs and query terms to `rank_documents_tf_idf_custom` to score and return the ranked list of document IDs.

## Function Reference (`ranking_bm25.py`)

- **`create_index_tfidf(data)`**: Builds the inverted index mapping terms to documents and positions, and calculates Term Frequency (TF), Document Frequency (DF), and Inverse Document Frequency (IDF). Returns the inverted index, TF lists, DF, IDF, and the preprocessed document index.
- **`rank_documents(terms, docs, index, idf, tf, document_index)`**: Calculates the cosine similarity (dot product) between the query vector and candidate document vectors using their normalized TF-IDF weights. Returns a sorted list of document IDs from most to least relevant.
- **`search_tf_idf(query, index, idf, tf, document_index)`**: Preprocesses the user's input query, filters for candidate documents that contain all terms in the query (Boolean AND search), and passes them to rank_documents for scoring. Returns the final ranked list.

For `create_index_tfidf`:
1. Preprocess the entire dataset using preprocess_doc to retrieve a clean document_index.
2. Loop through every document in the index and combine text fields (title, description, brand, sub_category, and product_details values) into a single full_text string, then split it into terms.
3. Build a local index that tracks the term frequencies and the array of positional indices for every word in the current document.
4. Calculate the document's L2 norm (the square root of the sum of squared term frequencies).
5. For each term in the local index, calculate the normalized TF (frequency divided by L2 norm), update the global Document Frequency (DF) counter, and append the document ID and positions to the global inverted index.
6. After processing all documents, compute the IDF for every unique term using the formula log(total_documents / df[term]).

For `rank_documents`:
1. Initialize a query_vector (a list of zeros) and a doc_vectors dictionary (mapping each candidate document ID to a list of zeros). Both vectors are sized to the number of terms in the query.
2. Count the frequency of each term in the query and compute the L2 norm (Euclidean norm) of these frequencies to normalize the query length.
3. Iterate through each term in the query along with its index position. If the term does not exist in the global index, skip it.
4. Calculate the query's TF-IDF score for the current term (Query TF = term count / query L2 norm, multiplied by the term's precomputed IDF) and assign it to the corresponding position in the query_vector.
5. Loop through the inverted index postings for the current term. If the document in the posting is present in the candidate docs list, calculate its TF-IDF score (the document's precomputed TF for that term multiplied by the term's IDF) and update the document's doc_vector at the current term's position.
6. Calculate the final score for each candidate document by computing the dot product (cosine similarity) between its populated doc_vector and the query_vector.
7. Pair each document ID with its computed score and sort the list in descending order so the most relevant documents appear at the top.
8. Extract and return the ordered list of document IDs.

For `search_tf_idf`:
1. Clean the query string using preprocess_line. Return an empty list if invalid.
2. Split the cleaned query into individual terms.
3. Iterate through each term and perform a strict conjunctive search (AND) by taking the set intersection (docs.intersection) of all documents containing the current term.
4. Return an empty list if any term is completely missing from the index or if the intersection becomes empty.
5. Pass the resulting candidate documents and the query terms to rank_documents to compute cosine similarity scores and return the ranked list.



## Function Reference (`test_retrival.py`)
- **`calculate_precision_at_k(retrieved_docs, relevant_docs, k)`**: Computes the proportion of the top K retrieved documents that are actually relevant. Returns hits / K.
- **`calculate_recall_at_k(retrieved_docs, relevant_docs, k)`**: Computes the proportion of all available relevant documents that were successfully retrieved in the top K. Returns hits / total_relevant_docs.
- **`calculate_f1_score_at_k(p_at_k, r_at_k)`**: Calculates the harmonic mean of Precision@K and Recall@K. Returns 0 if their sum is 0.
- **`calculate_average_precision(retrieved_docs, relevant_docs)`**: Computes Average Precision (AP) for a single query by averaging the precision at every rank where a relevant document is found.
- **`calculate_reciprocal_rank(retrieved_docs, relevant_docs)`**: Computes the Reciprocal Rank (RR) based on the position of the first relevant document retrieved (1 / rank).
- **`calculate_ndcg_at_k(retrieved_docs, relevant_docs, k)`**: Computes the Normalized Discounted Cumulative Gain (NDCG) at K by calculating the discounted gain of the actual ranking and dividing it by the Ideal DCG (IDCG).
- **`main()`**: Executes the evaluation metrics by loading the dataset, building the index, reading the validation CSV, executing queries, and calculating all cumulative and averaged metrics.

For `main`:
1. Define the absolute paths to the dataset and validation files using os.path, and set the target K value.
2. Load the JSON dataset and call create_index_tfidf to build the TF-IDF inverted index.
3. Load the validation CSV and establish a queries_map dictionary that links the numeric query_ids in the CSV to their corresponding textual search queries.
4. Group the validation dataframe by query_id to evaluate one specific search at a time.
5. For each query group, filter for rows where labels == 1 to extract a list of true relevant document IDs (pid).
6. Execute the search engine (search_tf_idf) using the mapped query text to retrieve a ranked list of candidate documents.
7. Call the individual metric functions (AP, RR, Precision, Recall, F1, NDCG) and add their results to cumulative total variables.
8. After processing all queries, divide the cumulative totals by the number of evaluated queries to print the final averaged metrics (Mean Average Precision, Mean Reciprocal Rank, etc.).


## Function Reference (`word2vec_ranking.py`)

- **`stable_hash(text)`**: Computes a deterministic CRC32 hash for a given text string so `gensim` initializes identical word vectors across different runs. Returns an integer hash value.
- **`get_doc_terms(record)`**: Extracts and concatenates the preprocessed text fields (`title`, `description`, `brand`, `sub_category`, and `product_details` values) of a product record and splits them into a list of terms.
- **`train_word2vec(document_index, params=W2V_PARAMS)`**: Trains a Skip-gram `Word2Vec` model on the corpus where each product's terms act as a sentence, using `stable_hash` and fixed parameters (`vector_size=100`, `window=5`, `min_count=1`, `sg=1`, `epochs=20`, `workers=1`) for reproducibility. Returns the trained model.
- **`text_to_vector(terms, model)`**: Converts a list of terms into a single dense document or query embedding by averaging the `Word2Vec` vectors of all known terms. Returns `None` if no terms exist in the model's vocabulary.
- **`build_doc_vectors(document_index, model)`**: Precomputes and caches the averaged `Word2Vec` embedding for every product in `document_index`. Returns a dictionary mapping `prod_id` to its vector.
- **`cosine_similarity(a, b)`**: Computes the cosine similarity between two dense vectors `a` and `b` using `np.dot(a, b) / (norm(a) * norm(b))`, returning `0.0` if either vector has zero norm.
- **`rank_documents_word2vec(query_terms, docs, doc_vectors, model)`**: Embeds the query terms via `text_to_vector`, computes cosine similarity against each candidate document's precomputed vector, and sorts matches by descending similarity (breaking ties by `doc_id`). Returns a list of `(doc_id, score)` tuples.
- **`search_word2vec_with_scores(query, index, document_index, model, doc_vectors)`**: Preprocesses the query, filters candidate documents using strict conjunctive search (Boolean AND), and ranks them via `rank_documents_word2vec`. Returns a list of `(doc_id, score)` tuples.
- **`search_word2vec(query, index, document_index, model, doc_vectors)`**: Wrapper around `search_word2vec_with_scores` that strips scores and returns only the ordered list of `doc_id`s so it matches the interface of `search_tf_idf` and `search_bm25`.
- **`evaluate_on_labels(queries_map, val_df, algorithms, k=10)`**: Runs a list of `(name, search_function, extra_args)` algorithms against a ground-truth DataFrame (`val_df`) and computes averaged `P@K`, `R@K`, `F1@K`, `MAP`, `MRR`, and `NDCG@K`. Returns a list of result dictionaries.
- **`main()`**: Loads the dataset, builds the TF-IDF inverted index, trains the `Word2Vec` model, prints top-20 results and overlap counts against TF-IDF and BM25 on the 5 test queries, and runs evaluation tables on both `validation_labels.csv` (`K=10, 20`) and `validation_labels_master.csv` (`K=20`).

For `train_word2vec`:
1. Iterate over all records in `document_index` and extract their token lists using `get_doc_terms`, discarding any empty documents.
2. Initialize and train `gensim.models.Word2Vec` with `sentences`, `hashfxn=stable_hash`, and `W2V_PARAMS`.
3. Return the trained `Word2Vec` model.

For `search_word2vec_with_scores`:
1. Clean the raw query string using `preprocess_line` and split it into `query_terms`; return an empty list if empty.
2. Perform a strict conjunctive search (Boolean AND) across `index`, intersecting the sets of document IDs containing each query term.
3. Return an empty list immediately if any term is missing from `index` or if the intersection is empty.
4. Pass `query_terms`, the matching candidate `docs`, `doc_vectors`, and `model` to `rank_documents_word2vec` and return the scored results.

For `evaluate_on_labels`:
1. Loop through each `(name, search_function, search_args)` tuple in `algorithms` and initialize cumulative metric totals (`P`, `R`, `F1`, `AP`, `RR`, `NDCG`).
2. Group `val_df` by `query_id`, extract relevant `pid`s where `labels == 1`, and execute `search_function` on the mapped query text.
3. Compute all six Part 2 evaluation metrics at cutoff `k` for each query and add them to the running totals.
4. Divide each cumulative total by `num_queries` and return the summary rows for tabular comparison.


## Function Reference (`representation_experiments.py`)

- **`weighted_vector(terms)`**: Computes an IDF-weighted average `Word2Vec` embedding for a list of terms by weighting each known term vector `model.wv[t]` by `idf.get(t, 0.0)`. Returns `None` if no terms are in the vocabulary or the total weight is zero.
- **`and_docs(q)`**: Preprocesses the query string `q` and performs strict conjunctive retrieval (Boolean AND) using the inverted index. Returns a tuple `(terms, docs)` containing the cleaned query tokens and the set of matching document IDs.
- **`make_search(kind)`**: Factory function that builds and returns a `search(q, *_)` callable for either `"weighted"` (IDF-weighted Word2Vec average) or `"d2v"` (Doc2Vec PV-DBOW inference), ranking candidate documents from `and_docs(q)` by cosine similarity.

For `weighted_vector`:
1. Iterate over each term in `terms` and check if it exists in `model.wv`.
2. Append the term's embedding `model.wv[t]` to `vecs` and its corpus IDF weight `idf.get(t, 0.0)` to `ws`.
3. If `vecs` is empty or `sum(ws) == 0`, return `None`.
4. Return the weighted average vector computed via `np.average(vecs, axis=0, weights=ws)`.

For `make_search`:
1. Accept a representation mode `kind` (`"weighted"` or `"d2v"`) and define an inner `search(q, *_)` function.
2. Retrieve `terms` and candidate `docs` via `and_docs(q)`.
3. If `kind == "weighted"`, compute the query vector with `weighted_vector(terms)` and look up precomputed IDF-weighted document vectors; otherwise seed `d2v.random.seed(42)`, infer the query vector with `d2v.infer_vector(terms, epochs=100)`, and fetch document vectors from `d2v.dv`.
4. Return an empty list if the query vector `qv` is `None`.
5. Compute `cosine_similarity(qv, vecs[p])` for every candidate document `p` in `docs`, sort by descending score (breaking ties by `doc_id`), and return the ranked list of document IDs.

For script execution (`__main__` block):
1. Load `fashion_products_dataset.json`, build the TF-IDF index, train `Word2Vec`, and precompute plain and IDF-weighted document vectors.
2. Wrap all products in `TaggedDocument` objects and train a `Doc2Vec` PV-DBOW model (`dm=0`, `dbow_words=1`, `vector_size=100`, `window=5`, `epochs=20`, `seed=42`, `workers=1`).
3. Load `validation_labels.csv` and evaluate four representations side by side (`TF-IDF`, `word2vec average`, `word2vec IDF-weighted`, and `Doc2Vec (PV-DBOW)`) using `evaluate_on_labels` for `K=10` and `K=20`, printing rounded comparison DataFrames[cite: 14, 15].


## AI usage
We used Gemini to review our ranking and evaluation code (BM25, custom scoring, Word2Vec, and representation experiments) and debug errors in it, to help write testing code, and to review our draft explanations of these decisions. We checked all the code and results ourselves and can explain every function.