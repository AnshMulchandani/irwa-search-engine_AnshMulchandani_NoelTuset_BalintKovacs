"""
Baseline vs improved RAG on the same queries (Part 4, RAG section).

Retrieval uses our Part 2 TF-IDF search (conjunctive AND), so both generators get real search results.
The baseline receives the raw query; the improved generator first removes price and rating phrases
(e.g. "under 800") so that AND retrieval is not broken by words that never appear in product text.

Run from the repository root:
    python project_progress/part_4/rag_comparison.py              # calls Groq (needs GROQ_API_KEY in .env)
    python project_progress/part_4/rag_comparison.py --dry-run    # no API calls: shows what each LLM would receive
Writes project_progress/part_4/rag_comparison_results.md
"""
import argparse
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "project_progress"))

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

from myapp.search.load_corpus import load_corpus
from myapp.generation.rag import RAGGenerator
from myapp.generation.rag_improved import ImprovedRAGGenerator, parse_constraints
from part_1.preprocess import get_json_data
import part_2.inverted_index as tf_idf

QUERIES = [
    ("women tshirt round neck cotton", "common query, thousands of matches"),
    ("ecko unl printed sweatshirt", "brand query"),
    ("satin necktie set pocket square cufflinks", "accessory set"),
    ("men slim jeans blue under 800", "price limit written in the query"),
    ("cheap men solid blue track pants", "soft preference: low price"),
    ("women sweatshirt rating above 4", "rating limit written in the query"),
    ("men formal shirt under 200", "price limit that no product meets"),
    ("waterproof hiking boots", "nothing in the catalogue matches"),
]


def retrieve(query, index, idf, tf, document_index, corpus, k=20):
    pids = tf_idf.search_tf_idf(query, index, idf, tf, document_index)[:k]
    return [corpus[p] for p in pids if p in corpus]


def baseline_context(results, top_n=20):
    """Exactly what the baseline puts in its prompt."""
    return "\n".join(f"- PID: {r.pid}, Title: {r.title}" for r in results[:top_n])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="do not call the LLM; record the prompts only")
    args = ap.parse_args()
    key = os.environ.get("GROQ_API_KEY", "")
    dry = args.dry_run or not key or key.startswith("<")
    if dry and not args.dry_run:
        print("No GROQ_API_KEY in .env: running in --dry-run mode.")

    data_file = os.path.join(ROOT, "data", "fashion_products_dataset.json")
    print("Loading corpus and building the TF-IDF index...")
    corpus = load_corpus(data_file)
    index, tf, df, idf, document_index = tf_idf.create_index_tfidf(get_json_data(data_file))

    baseline = RAGGenerator()
    improved = ImprovedRAGGenerator(corpus=corpus)

    out = ["# RAG comparison: baseline vs improved", "",
           f"Model: `{os.environ.get('GROQ_MODEL', 'llama-3.1-8b-instant')}`. "
           f"Mode: {'dry run (no LLM calls)' if dry else 'live'}. Retrieval: Part 2 TF-IDF, AND semantics, top 20.", ""]

    for query, why in QUERIES:
        print(f"\n=== {query}")
        c = parse_constraints(query)
        base_results = retrieve(query, index, idf, tf, document_index, corpus)
        imp_results = retrieve(c["clean_query"], index, idf, tf, document_index, corpus)

        prompt, early, cands = improved.build_prompt(query, imp_results)
        out += [f"## `{query}`", f"*{why}*", "",
                f"- Baseline retrieval (raw query): **{len(base_results)}** products",
                f"- Improved retrieval (query `{c['clean_query']}`): **{len(imp_results)}** products, "
                f"**{len(cands)}** shown to the LLM after de-duplication and constraints", ""]

        if dry:
            base_answer = "(dry run)"
            imp_answer = early if early is not None else "(dry run: LLM would be called with the prompt below)"
        else:
            t0 = time.time(); base_answer = baseline.generate_response(query, base_results); t1 = time.time()
            imp_answer = improved.generate_response(query, imp_results); t2 = time.time()
            out.append(f"Latency: baseline {t1 - t0:.1f}s, improved {t2 - t1:.1f}s")
            out.append("")

        out += ["**Baseline answer**", "", "```", str(base_answer).strip(), "```", "",
                "**Improved answer**", "", "```", str(imp_answer).strip(), "```", "",
                "<details><summary>What each LLM sees</summary>", "",
                "Baseline context:", "```", baseline_context(base_results) or "(empty)", "```",
                "Improved prompt:", "```", prompt or "(no LLM call: answered by the gate)", "```", "</details>", ""]
        print("baseline:", str(base_answer)[:200].replace("\n", " "))
        print("improved:", str(imp_answer)[:200].replace("\n", " "))

    path = os.path.join(os.path.dirname(__file__), "rag_comparison_results.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"\nWrote {path}")


if __name__ == "__main__":
    main()
