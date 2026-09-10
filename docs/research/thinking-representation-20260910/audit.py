"""Offline lexical/accounting census. No model, translation, or network calls.

Requires tiktoken. This measures supplied strings, not private reasoning.
Run with --write to refresh AUDIT.json; otherwise verify the saved census.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import importlib.metadata
import json
import zlib

import tiktoken


PAIRS = [
    ("comparison", "x >= 0", "x ≥ 0"),
    ("inequality", "x != y", "x ≠ y"),
    ("conjunction", "a and b", "a ∧ b"),
    ("negation", "not p", "¬p"),
    ("arrow", "x -> y", "x → y"),
    ("equivalence", "x iff y", "x ⇔ y"),
    ("math italic", "x", "𝑥"),
    ("math script", "x", "𝓍"),
    ("Greek name", "alpha", "α"),
]
CONTRACTS = {
    "English prose": "The value is not null and the count is at least 10.",
    "code notation": "value != null and count >= 10",
    "modern Chinese": "值非空且数量至少为10。",
    "Wenyan-like shorthand": "值非空，数不少于十。",
    "Russian": "Значение не null, а количество не меньше 10.",
    "Turkish": "Değer null değil ve sayı en az 10.",
}
# Manually transcribed Table 2 of arXiv:2604.14210, read 2026-09-10.
# Means are printed as integers; nearest-integer rounding is an explicit
# assumption for the interval-overlap calculation, not an author guarantee.
CODING_TABLE = {
    "MiniMax-2.7": {
        "en": {"n": 50, "input": 298720, "output": 61762, "reasoning": 22368},
        "zh": {"n": 39, "input": 382974, "output": 79182, "reasoning": 28677},
    },
    "GPT-5.4-mini": {
        "en": {"n": 50, "input": 84347, "output": 2695, "reasoning": 0},
        "zh": {"n": 46, "input": 91681, "output": 2929, "reasoning": 0},
    },
    "GLM-5": {
        "en": {"n": 48, "input": 1417012, "output": 112803, "reasoning": 87474},
        "zh": {"n": 49, "input": 1388094, "output": 110501, "reasoning": 85688},
    },
}


def census():
    encodings = {n: tiktoken.get_encoding(n) for n in ("o200k_base", "cl100k_base")}

    def count(text):
        return {
            "text": text,
            "characters": len(text),
            "utf8_bytes": len(text.encode("utf-8")),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "tokens": {n: len(e.encode(text)) for n, e in encodings.items()},
        }

    table_audit = []
    for model, arms in CODING_TABLE.items():
        en, zh = arms["en"], arms["zh"]
        for metric in ("input", "output", "reasoning"):
            left, right = en[metric] * en["n"], zh[metric] * zh["n"]
            table_audit.append({
                "model": model, "metric": metric,
                "inferred_en_total_from_rounded_mean": left,
                "inferred_zh_total_from_rounded_mean": right,
                "absolute_total_difference": abs(left - right),
                "same_total_possible_under_nearest_integer_rounding":
                    abs(left - right) <= (en["n"] + zh["n"]) / 2,
                "reported_mean_ratio_zh_over_en": zh[metric] / en[metric] if en[metric] else None,
                "inverse_sample_count_ratio": en["n"] / zh["n"],
            })

    original = CONTRACTS["English prose"].encode("utf-8")
    encoded = base64.b64encode(original).decode("ascii")
    packed = base64.b64encode(zlib.compress(original)).decode("ascii")
    assert base64.b64decode(encoded) == original
    assert zlib.decompress(base64.b64decode(packed)) == original
    return {
        "classification": "OBSERVED_OFFLINE_LEXICAL_AND_PUBLISHED_TABLE_ARITHMETIC",
        "tiktoken_version": importlib.metadata.version("tiktoken"),
        "native_model_calls": 0,
        "native_thinking_token_savings": None,
        "semantic_or_workflow_parity_established": False,
        "limitations": [
            "Illustrative manually authored strings; not representative language samples.",
            "Translations and symbolic forms are not certified equivalents for every domain.",
            "Tokenizer identities are proxies, not verified Astra/Sol/Luna internal tokenizers.",
            "No model-internal language, reasoning trace, or native cost was observed.",
            "Binary round-trip exactness does not establish model comprehension or economics.",
            "Published table anomaly does not establish its cause without raw receipts.",
        ],
        "notation_pairs": [{"label": n, "ordinary": count(a), "alternative": count(b)} for n, a, b in PAIRS],
        "contract_variants": {n: count(s) for n, s in CONTRACTS.items()},
        "reversible_encodings": {"original": count(original.decode()), "base64": count(encoded), "zlib_base64": count(packed)},
        "coding_language_table_source": "https://arxiv.org/html/2604.14210",
        "coding_language_table_transcription": CODING_TABLE,
        "coding_language_table_audit": table_audit,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    target = Path(__file__).with_name("AUDIT.json")
    result = census()
    if args.write:
        target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    else:
        assert json.loads(target.read_text()) == result, "Census drift; inspect before refreshing"
    print(json.dumps({"status": "WRITTEN" if args.write else "REPRODUCED", "notation_pairs": len(PAIRS), "contract_variants": len(CONTRACTS), "table_rows": len(result["coding_language_table_audit"]), "native_calls": 0}))
