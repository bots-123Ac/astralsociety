"""
Word loader using wordfreq — real common English words.
Filters to 4/5/6 letter pure alphabetic words.
"""
import random
from wordfreq import top_n_list

print("📚 Loading English word pool...")

# Load top 50,000 most common English words (frequency sorted)
_TOP_WORDS = top_n_list('en', 50000)

# Build pools by length
WORD_POOL = {4: [], 5: [], 6: []}
_seen = set()

for _w in _TOP_WORDS:
    _w = _w.lower().strip()
    if not _w.isalpha() or not _w.isascii():
        continue
    if _w in _seen:
        continue
    if 4 <= len(_w) <= 6:
        WORD_POOL[len(_w)].append(_w)
        _seen.add(_w)

print(f"✅ Words loaded: 4L={len(WORD_POOL[4])}, 5L={len(WORD_POOL[5])}, 6L={len(WORD_POOL[6])}")


def get_random_word(length: int) -> str:
    """Return a random common English word of given length."""
    pool = WORD_POOL.get(length, [])
    if not pool:
        return {4: "star", 5: "apple", 6: "planet"}.get(length, "apple")
    return random.choice(pool)


def is_valid_word(word: str, length: int) -> bool:
    """Check if the guessed word is a real word (optional validation)."""
    word = word.lower().strip()
    if len(word) != length or not word.isalpha():
        return False
    return word in WORD_POOL.get(length, [])


def words_count() -> dict:
    """Return count of words per length."""
    return {k: len(v) for k, v in WORD_POOL.items()}
