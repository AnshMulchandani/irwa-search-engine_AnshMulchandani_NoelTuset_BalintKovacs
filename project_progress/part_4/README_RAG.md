# Part 4: RAG improvements (Bálint)

The baseline generator is `myapp/generation/rag.py` (`RAGGenerator`). The improved one is
`myapp/generation/rag_improved.py` (`ImprovedRAGGenerator`), a drop-in replacement with the same
`generate_response(user_query, retrieved_results, top_N)` call.

## Setup
1. `pip install -r requirements.txt`
2. Put your own Groq key in `.env`: `GROQ_API_KEY = 'gsk_...'`. **Do not commit it**: `.env` is tracked
   in this public repo. Run `git update-index --assume-unchanged .env` once, or `git rm --cached .env`.
3. Optional: `RAG_MODE = "baseline"` in `.env` switches the web app back to the original generator.
   The default is the improved one.

## Run
From the repository root:

| Command | What it does |
|---|---|
| `python web_app.py` | Web app on port 8088, using the improved RAG on the results page |
| `python project_progress/part_4/rag_comparison.py` | Baseline vs improved on 8 queries; writes `rag_comparison_results.md` |
| `python project_progress/part_4/rag_comparison.py --dry-run` | Same without API calls: records what each LLM would receive |
| `python project_progress/part_4/test_rag_improved.py` | Offline checks with a fake LLM (no key needed) |

## Weaknesses of the baseline
1. **The LLM only sees PID and title.** It cannot justify a choice by price, rating, material or stock, so
   its "Why" is generic or invented. Our titles are also highly repetitive (28,080 products, 5,953 distinct titles).
2. **Twenty near-identical titles.** The same product is often listed several times; the prompt is long and the
   options look the same.
3. **Price and rating limits break retrieval.** With AND semantics, "under 800" requires the words "under" and
   "800" in the product text, so the baseline gets an empty result list and the LLM answers with nothing to go on.
4. **"No good products" depends on the LLM.** Nothing stops it from recommending a product that violates the
   request, and with an empty list it can invent one.
5. **No grounding controls.** No system message, default sampling temperature, no length limit, and no check
   that the recommended PID was actually retrieved.

## Improvements
| # | Improvement | Pros | Cons |
|---|---|---|---|
| 1 | **Rich, de-duplicated context**: brand, price, original price and discount, rating (or "no rating listed"), stock, up to 6 useful product details (codes such as Style Code excluded) and a short description; listings with the same title, brand and price are merged; top 8 kept | Answers can cite real numbers; fewer repeated options; shorter list | Longer prompt per product (more tokens, slightly higher latency); merging can hide a size or colour variant |
| 2 | **Constraint parsing and a "no good products" gate**: price limits ("under 800", "between 500 and 1000"), rating limits ("rating above 4", "4+ stars") and preferences ("cheap", "top rated") are read from the query, removed before retrieval and applied to the results. If nothing is retrieved, or nothing meets the limits, a fixed answer explains why, without calling the LLM | Queries with limits now return results; impossible requests get an honest answer with the reason (e.g. cheapest is ₹499); no API cost and no hallucination in those cases | Rule-based: phrasings the regular expressions do not cover are not understood; prices are assumed to be in rupees |
| 3 | **Grounded prompt and output check**: system message that forbids invented facts, temperature 0.2, at most 300 tokens, a fixed answer format with an alternative and its trade-off, and a check that every PID in the answer was in the list (otherwise the top search result is returned with a note) | More consistent, shorter answers; invented products cannot reach the user | Lower temperature makes answers more uniform; the PID check only catches invented IDs, not wrong claims about real products |
