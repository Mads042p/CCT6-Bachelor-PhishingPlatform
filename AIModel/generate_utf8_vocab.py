"""Generate a vocabulary JSON mapping letters and digits to their UTF-8 codepoints.

This creates `vocabletters.json` in the same folder with the following format:
{
  "<pad>": 0,
  "<unk>": 1,
  "a": 97,
  "A": 65,
  "0": 48,
  ...
}

Note: the values after PAD/UNK are the Unicode code points (integers from `ord(char)`).
If you plan to use this mapping with an `nn.Embedding`, be aware embedding indices must be in range
`[0, vocab_size-1]`. Using raw code points will require setting `vocab_size` to at least
`max(codepoint) + 1` or remapping codepoints to a dense index range in your model.
"""
import json
import os
from typing import List


OUTPUT_FILE = "vocabletters.json"


def build_utf8_vocab(include_lower=True, include_upper=True, include_digits=True, extra_chars: List[str]=None):
    vocab = {"<pad>": 0, "<unk>": 1}

    if include_lower:
        for c in [chr(i) for i in range(ord('a'), ord('z') + 1)]:
            vocab[c] = ord(c)

    if include_upper:
        for c in [chr(i) for i in range(ord('A'), ord('Z') + 1)]:
            vocab[c] = ord(c)

    if include_digits:
        for c in [chr(i) for i in range(ord('0'), ord('9') + 1)]:
            vocab[c] = ord(c)

    if extra_chars:
        for c in extra_chars:
            if c not in vocab:
                vocab[c] = ord(c)

    return vocab


def save_vocab(vocab: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=2, ensure_ascii=False)


def main():
    here = os.path.dirname(__file__)
    out_path = os.path.join(here, OUTPUT_FILE)

    # adjust flags if you want a different set of characters
    vocab = build_utf8_vocab(include_lower=True, include_upper=True, include_digits=True,
                             extra_chars=["@", ".", "-", "_", "/", ":"])

    save_vocab(vocab, out_path)
    print(f"Wrote UTF-8 vocabulary to: {out_path} (entries: {len(vocab)})")


if __name__ == "__main__":
    main()
