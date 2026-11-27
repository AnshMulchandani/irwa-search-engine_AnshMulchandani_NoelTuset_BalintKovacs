"""
Improved RAG generator (Part 4).

Drop-in replacement for RAGGenerator: same generate_response(user_query, retrieved_results, top_N) call,
returns a string. Three improvements over the baseline:

1. Rich, de-duplicated product context: the LLM sees brand, price, discount, rating, stock and key
   product details for each product, not just PID + title. Near-identical listings are merged.
2. Query constraints + a "no good products" gate: price and rating limits in the query ("under 800",
   "4+ stars") are parsed and applied before the LLM is called. If nothing is retrieved, or nothing
   satisfies the constraints, a deterministic answer is returned without calling the LLM.
3. Grounded prompt + output check: a system message that forbids inventing facts, a low temperature,
   a length limit, and a check that every PID in the answer was actually retrieved.
"""
import os
import re

from dotenv import load_dotenv

load_dotenv()

NO_GOOD_PRODUCTS = "There are no good products that fit the request based on the retrieved results."

# product_details keys that tell a shopper something; codes such as "Style Code" are left out
USEFUL_DETAIL_KEYS = ["Ideal For", "Fabric", "Fit", "Pattern", "Color", "Sleeve", "Neck Type", "Neck",
                      "Type", "Occasion", "Pack of", "Closure", "Suitable For"]

PRICE_WORD = r"(?:rs\.?|inr|₹)?\s*"
NUMBER = r"(\d+(?:[.,]\d+)*)"


def _to_number(text):
    return float(text.replace(",", ""))


def parse_constraints(query: str) -> dict:
    """
    Reads price and rating limits and soft preferences from a free-text query.
    Returns a dict with max_price, min_price, min_rating, prefer_cheap, prefer_rated, and
    clean_query: the query with the constraint phrases removed, so AND retrieval is not
    broken by words like "under" or "800" that never appear in product text.
    """
    q = query.lower()
    c = {"max_price": None, "min_price": None, "min_rating": None,
         "prefer_cheap": False, "prefer_rated": False}
    spans = []

    def grab(pattern, handler):
        for m in re.finditer(pattern, q):
            if any(m.start() < e and s0 < m.end() for s0, e in spans):
                continue  # already used by an earlier rule (e.g. "rating above 4" is not a price)
            handler(m)
            spans.append(m.span())

    # ratings first, so "rating above 4" is never read as a price of 4
    grab(r"\b(?:rating|rated)\s*(?:of\s*)?(?:above|over|at least|>=?|\+)?\s*(\d(?:\.\d)?)\b\s*(?:stars?|\+)?",
         lambda m: c.update(min_rating=float(m.group(1))))
    grab(r"\b(?:at least\s+|over\s+|above\s+)?(\d(?:\.\d)?)\s*(?:\+\s*)?stars?\b(?:\s*(?:and|or)\s*(?:above|up|more))?",
         lambda m: c.update(min_rating=float(m.group(1))))
    grab(rf"\bbetween\s+{PRICE_WORD}{NUMBER}\s+(?:and|-|to)\s+{PRICE_WORD}{NUMBER}",
         lambda m: c.update(min_price=_to_number(m.group(1)), max_price=_to_number(m.group(2))))
    grab(rf"\b(?:under|below|less than|cheaper than|max(?:imum)?|up to|upto|within)\s+{PRICE_WORD}{NUMBER}",
         lambda m: c.update(max_price=_to_number(m.group(1))))
    grab(rf"\b(?:over|above|more than|min(?:imum)?|at least)\s+{PRICE_WORD}{NUMBER}",
         lambda m: c.update(min_price=_to_number(m.group(1))))
    grab(r"\b(?:cheap|cheapest|budget|affordable|low[- ]cost|inexpensive)\b",
         lambda m: c.update(prefer_cheap=True))
    grab(r"\b(?:best[- ]rated|top[- ]rated|highly rated|well rated|good (?:rating|reviews?)|best reviewed)\b",
         lambda m: c.update(prefer_rated=True))

    # rebuild the query without the matched phrases
    keep, last = [], 0
    for start, end in sorted(spans):
        if start >= last:
            keep.append(q[last:start])
            last = end
    keep.append(q[last:])
    clean = re.sub(r"\b(?:with|and|for|price|priced|rs|inr)\b\s*$", "", " ".join("".join(keep).split())).strip()
    c["clean_query"] = clean if clean else query
    return c


def _get(doc, field):
    return getattr(doc, field, None) if not isinstance(doc, dict) else doc.get(field)


class ImprovedRAGGenerator:

    SYSTEM_PROMPT = (
        "You are a careful shopping assistant for a fashion e-commerce site. "
        "You only use the product facts given to you. Never invent prices, ratings, materials, "
        "brands or product IDs. If a fact is missing, say it is not listed."
    )

    PROMPT_TEMPLATE = """## User request
{user_query}

## What the user asked for, read from the request
{constraint_summary}

## Retrieved products (ranked by our search engine, best match first)
{product_block}

## Instructions
1. Check each product against the request: product type, gender, colour, material and any price or rating limit.
2. Pick the single best product. Prefer, in this order: matches the request, in stock, higher rating, better price.
3. Answer in this exact format, at most 120 words:
- Best Product: [PID] [title]
- Why: one or two sentences that cite the facts above (price, discount, rating, material, fit).
- Alternative: [PID] [title], and the trade-off compared with the best product (for example cheaper but lower rated). Leave out if none.
- Note: only if important information is missing (for example no rating listed).
4. Use only PIDs from the list above.
5. If no product matches the request, answer with exactly: "{no_good}"
"""

    def __init__(self, corpus=None, top_k=8, temperature=0.2, max_tokens=300, client=None):
        """
        corpus: optional {pid: Document} dict; used to fill in fields when the search results only carry pid and title.
        top_k: number of products shown to the LLM after filtering and de-duplication.
        client: optional object with the Groq chat.completions.create interface (used for tests).
        """
        self.corpus = corpus
        self.top_k = top_k
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = client
        self.last_prompt = None      # kept for the report and for debugging
        self.last_candidates = []

    # ---------- improvement 1: rich, de-duplicated context ----------

    def _full_doc(self, doc):
        """Returns the full corpus record for a search result, if a corpus was given."""
        pid = _get(doc, "pid")
        if self.corpus is not None and pid in self.corpus:
            return self.corpus[pid]
        return doc

    @staticmethod
    def _dedupe(docs):
        """Merges listings that are the same product (same title, brand and selling price), keeping the best ranked one."""
        seen, out = set(), []
        for d in docs:
            key = ((_get(d, "title") or "").strip().lower(), (_get(d, "brand") or "").strip().lower(), _get(d, "selling_price"))
            if key in seen:
                continue
            seen.add(key)
            out.append(d)
        return out

    @staticmethod
    def format_product(rank, doc):
        """One compact, factual block per product."""
        price = _get(doc, "selling_price")
        mrp = _get(doc, "actual_price")
        discount = _get(doc, "discount")
        rating = _get(doc, "average_rating")
        details = _get(doc, "product_details") or {}
        if isinstance(details, list):
            merged = {}
            for item in details:
                if isinstance(item, dict):
                    merged.update(item)
            details = merged
        facts = [f"{k}: {details[k]}" for k in USEFUL_DETAIL_KEYS if details.get(k)]
        description = " ".join((_get(doc, "description") or "").split())
        if len(description) > 180:
            description = description[:177].rsplit(" ", 1)[0] + "..."

        price_txt = f"₹{price:,.0f}" if price is not None else "price not listed"
        if mrp is not None and price is not None and mrp > price:
            price_txt += f" (was ₹{mrp:,.0f}" + (f", {discount:.0f}% off)" if discount is not None else ")")
        rating_txt = f"{rating:.1f}/5" if rating is not None else "no rating listed"
        stock_txt = "OUT OF STOCK" if _get(doc, "out_of_stock") else "in stock"

        lines = [f"[{rank}] PID {_get(doc, 'pid')} | {_get(doc, 'title')}",
                 f"    Brand: {_get(doc, 'brand') or 'not listed'} | Price: {price_txt} | Rating: {rating_txt} | {stock_txt}"]
        if facts:
            lines.append("    " + " | ".join(facts[:6]))
        if description:
            lines.append(f"    Description: {description}")
        return "\n".join(lines)

    # ---------- improvement 2: constraints and the "no good products" gate ----------

    @staticmethod
    def apply_constraints(docs, c):
        """Hard limits remove products; soft preferences only reorder. Returns (kept, reason_if_empty)."""
        kept = []
        for d in docs:
            price, rating = _get(d, "selling_price"), _get(d, "average_rating")
            if c["max_price"] is not None and (price is None or price > c["max_price"]):
                continue
            if c["min_price"] is not None and (price is None or price < c["min_price"]):
                continue
            if c["min_rating"] is not None and (rating is None or rating < c["min_rating"]):
                continue
            kept.append(d)

        # out-of-stock products go to the end, but are kept if nothing else is left
        kept.sort(key=lambda d: bool(_get(d, "out_of_stock")))
        if c["prefer_cheap"]:
            kept.sort(key=lambda d: (bool(_get(d, "out_of_stock")), _get(d, "selling_price") if _get(d, "selling_price") is not None else float("inf")))
        elif c["prefer_rated"]:
            kept.sort(key=lambda d: (bool(_get(d, "out_of_stock")), -(_get(d, "average_rating") or 0)))

        reason = None
        if docs and not kept:
            prices = [p for p in (_get(d, "selling_price") for d in docs) if p is not None]
            ratings = [r for r in (_get(d, "average_rating") for d in docs) if r is not None]
            parts = []
            if c["max_price"] is not None and prices:
                parts.append(f"the cheapest retrieved product costs ₹{min(prices):,.0f}, above your limit of ₹{c['max_price']:,.0f}")
            if c["min_price"] is not None and prices:
                parts.append(f"the most expensive retrieved product costs ₹{max(prices):,.0f}, below ₹{c['min_price']:,.0f}")
            if c["min_rating"] is not None:
                parts.append(f"the best rating among them is {max(ratings):.1f}/5" if ratings else "none of them has a rating")
            reason = "; ".join(parts) if parts else None
        return kept, reason

    @staticmethod
    def constraint_summary(c):
        parts = []
        if c["min_price"] is not None or c["max_price"] is not None:
            lo = f"₹{c['min_price']:,.0f}" if c["min_price"] is not None else "any"
            hi = f"₹{c['max_price']:,.0f}" if c["max_price"] is not None else "any"
            parts.append(f"price between {lo} and {hi}")
        if c["min_rating"] is not None:
            parts.append(f"rating of at least {c['min_rating']:.1f}/5")
        if c["prefer_cheap"]:
            parts.append("prefers a low price")
        if c["prefer_rated"]:
            parts.append("prefers a high rating")
        return "; ".join(parts) if parts else "no price or rating limits"

    # ---------- improvement 3: grounded generation and output check ----------

    def _client_or_new(self):
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        return self._client

    @staticmethod
    def check_pids(answer, allowed_pids):
        """Returns the product IDs in the answer that were not in the list given to the LLM."""
        mentioned = set(re.findall(r"\b[A-Z0-9]{16}\b", answer or ""))
        return sorted(mentioned - set(allowed_pids))

    def build_prompt(self, user_query, retrieved_results, top_N=20):
        """Runs steps 1 and 2 and returns (prompt or None, early_answer or None, candidates)."""
        c = parse_constraints(user_query)
        docs = [self._full_doc(d) for d in (retrieved_results or [])[:top_N]]
        if not docs:
            return None, ("No products matched every word of your search. "
                          "Try fewer or more general words (for example drop the colour or the brand)."), []
        docs = self._dedupe(docs)
        kept, reason = self.apply_constraints(docs, c)
        if not kept:
            msg = NO_GOOD_PRODUCTS
            if reason:
                msg += f" ({reason}.)"
            return None, msg, []
        candidates = kept[:self.top_k]
        block = "\n".join(self.format_product(i + 1, d) for i, d in enumerate(candidates))
        prompt = self.PROMPT_TEMPLATE.format(user_query=user_query, constraint_summary=self.constraint_summary(c),
                                             product_block=block, no_good=NO_GOOD_PRODUCTS)
        return prompt, None, candidates

    def generate_response(self, user_query: str, retrieved_results: list, top_N: int = 20) -> str:
        DEFAULT_ANSWER = "RAG is not available. Check your credentials (.env file) or account limits."
        prompt, early, candidates = self.build_prompt(user_query, retrieved_results, top_N)
        self.last_prompt, self.last_candidates = prompt, candidates
        if early is not None:
            return early      # no LLM call: nothing to recommend, so nothing to hallucinate
        try:
            client = self._client_or_new()
            completion = client.chat.completions.create(
                model=os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant"),
                messages=[{"role": "system", "content": self.SYSTEM_PROMPT},
                          {"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            answer = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during RAG generation: {e}")
            return DEFAULT_ANSWER

        invented = self.check_pids(answer, [_get(d, "pid") for d in candidates])
        if invented:
            top = candidates[0]
            return (f"- Best Product: {_get(top, 'pid')} {_get(top, 'title')}\n"
                    f"- Why: it is the best match found by the search engine for your request.\n"
                    f"- Note: the generated answer referred to products that were not retrieved "
                    f"({', '.join(invented)}), so it was replaced by the top search result.")
        return answer
