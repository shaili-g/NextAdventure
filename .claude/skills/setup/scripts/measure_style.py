"""Measure someone's writing from samples, for Profile/Writing Style.md.

Usage: python3 measure_style.py <sample1.txt> [sample2.txt ...]

Prints JSON: words, sentences, sentence length (median, mean, 90th percentile), contractions,
semicolons, em/en dashes, colons, exclamation marks and questions per 1,000 words, and how often
"I", "we" and "you" appear. Paste samples into .txt files first (one per piece of writing).
"""
import json
import re
import statistics
import sys
from pathlib import Path

CONTRACTION = re.compile(r"\b\w+(?:'|’)(?:s|re|ve|ll|d|t|m)\b", re.I)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    text = "\n".join(Path(p).read_text() for p in sys.argv[1:])
    text = re.sub(r"https?://\S+", "", text)
    words = re.findall(r"[A-Za-z’']+", text)
    n = len(words) or 1
    sentences = [s for s in re.split(r"(?<=[.!?])\s+|\n{2,}", text) if re.search(r"[A-Za-z]", s)]
    lengths = sorted(len(re.findall(r"[A-Za-z’']+", s)) for s in sentences)
    per_k = lambda c: round(c * 1000 / n, 1)
    low = [w.lower() for w in words]
    out = {
        "samples": len(sys.argv) - 1,
        "words": len(words),
        "sentences": len(lengths),
        "sentence_words_median": statistics.median(lengths) if lengths else 0,
        "sentence_words_mean": round(statistics.mean(lengths), 1) if lengths else 0,
        "sentence_words_p90": lengths[int(len(lengths) * 0.9) - 1] if lengths else 0,
        "per_1000_words": {
            "contractions": per_k(len(CONTRACTION.findall(text))),
            "semicolons": per_k(text.count(";")),
            "em_or_en_dashes": per_k(text.count("—") + text.count("–") + len(re.findall(r"\s--\s", text))),
            "colons": per_k(len(re.findall(r":(?!//)", text))),
            "exclamations": per_k(text.count("!")),
            "questions": per_k(text.count("?")),
        },
        "person_per_1000_words": {"I": per_k(low.count("i")), "we": per_k(low.count("we")),
                                  "you": per_k(low.count("you"))},
        "note": "Under 800 words is too little to measure well; say so in the style file.",
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
