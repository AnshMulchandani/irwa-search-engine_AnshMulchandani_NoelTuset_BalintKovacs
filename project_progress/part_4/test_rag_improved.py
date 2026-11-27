"""
Offline checks for the improved RAG generator: no API key needed (the LLM is replaced by a fake client).
Run from the repository root:  python project_progress/part_4/test_rag_improved.py
"""
import os
import sys
from types import SimpleNamespace

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from myapp.search.objects import Document
from myapp.generation.rag_improved import ImprovedRAGGenerator, parse_constraints, NO_GOOD_PRODUCTS


class FakeClient:
    """Mimics groq.Groq: returns a fixed answer and records the request."""
    def __init__(self, answer):
        self.answer, self.calls = answer, []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.answer))])


def doc(pid, title, price, rating=None, stock=True, brand="Acme"):
    return Document(pid=pid, title=title, brand=brand, selling_price=price, actual_price=price * 2, discount=50,
                    average_rating=rating, out_of_stock=not stock, description="Soft cotton blend fabric.",
                    product_details=[{"Fabric": "Cotton Blend"}, {"Style Code": "X1"}, {"Ideal For": "Men"}])


A = doc("AAAAAAAAAAAAAAA1", "Slim Men Blue Jeans", 699, 4.1)
B = doc("BBBBBBBBBBBBBBB2", "Slim Men Blue Jeans", 699, 4.1)          # same product listed twice
C = doc("CCCCCCCCCCCCCCC3", "Skinny Men Blue Jeans", 1299, 3.6)
D = doc("DDDDDDDDDDDDDDD4", "Slim Men Dark Blue Jeans", 549, None, stock=False)


def test_parser():
    c = parse_constraints("men slim jeans blue under 800")
    assert c["max_price"] == 800 and c["clean_query"] == "men slim jeans blue"
    c = parse_constraints("women sweatshirt rating above 4")
    assert c["min_rating"] == 4 and c["min_price"] is None and c["clean_query"] == "women sweatshirt"
    assert parse_constraints("cheap track pants")["prefer_cheap"]


def test_context_is_rich_and_deduplicated():
    gen = ImprovedRAGGenerator(client=FakeClient("x"))
    prompt, early, cands = gen.build_prompt("men slim jeans blue", [A, B, C, D])
    assert early is None
    assert [d.pid for d in cands] == [A.pid, C.pid, D.pid]          # B merged into A; out of stock last
    assert "₹699 (was ₹1,398, 50% off)" in prompt and "4.1/5" in prompt
    assert "no rating listed" in prompt and "OUT OF STOCK" in prompt
    assert "Fabric: Cotton Blend" in prompt and "Style Code" not in prompt


def test_constraint_gate_skips_llm():
    fake = FakeClient("should not be called")
    gen = ImprovedRAGGenerator(client=fake)
    answer = gen.generate_response("men slim jeans blue under 300", [A, C])
    assert answer.startswith(NO_GOOD_PRODUCTS) and "₹699" in answer and fake.calls == []
    answer = gen.generate_response("anything", [])
    assert "No products matched" in answer and fake.calls == []


def test_price_filter_and_generation_settings():
    fake = FakeClient(f"- Best Product: {A.pid} Slim Men Blue Jeans\n- Why: ₹699, rated 4.1/5.")
    gen = ImprovedRAGGenerator(client=fake)
    answer = gen.generate_response("men slim jeans blue under 800", [A, C, D])
    sent = fake.calls[0]
    assert sent["temperature"] == 0.2 and sent["messages"][0]["role"] == "system"
    assert C.pid not in sent["messages"][1]["content"]                # ₹1,299 is over the limit
    assert answer.startswith("- Best Product: " + A.pid)


def test_invented_pid_is_caught():
    fake = FakeClient("- Best Product: ZZZZZZZZZZZZZZZ9 Imaginary Jeans")
    gen = ImprovedRAGGenerator(client=fake)
    answer = gen.generate_response("men slim jeans blue", [A, C])
    assert A.pid in answer and "ZZZZZZZZZZZZZZZ9" in answer and "replaced by the top search result" in answer


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("passed:", name)
