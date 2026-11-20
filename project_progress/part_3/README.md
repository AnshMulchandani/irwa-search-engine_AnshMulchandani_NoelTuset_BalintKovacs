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

## AI usage
We used Gemini to review our evaluation and inverted_index code and debug errors in it, to help write some parts of the code like how to do certain computations, certain ranking decisions and help build testing code, and to review our draft explanation of these decisions. We checked the code and the results ourselves and can explain every function.