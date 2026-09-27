"""
Word loader using wordfreq — real common English words.
Falls back to built-in list if wordfreq fails.
"""
import random

WORD_POOL = {4: [], 5: [], 6: []}

# ═══════════════════════════════════════════════
# FALLBACK WORD LIST (if wordfreq fails)
# ═══════════════════════════════════════════════
FALLBACK_WORDS = {
    4: [
        "word", "game", "book", "love", "time", "rain", "fire", "blue", "star", "moon",
        "gold", "leaf", "song", "fish", "bird", "door", "road", "tree", "wind", "snow",
        "king", "hope", "dark", "warm", "wild", "calm", "fear", "dare", "gift", "life",
        "mind", "soul", "luck", "hero", "wolf", "lion", "bear", "deer", "cold", "cool",
        "fast", "slow", "high", "deep", "thin", "wide", "long", "hard", "soft", "rich",
    ],
    5: [
        "apple", "house", "light", "water", "happy", "music", "earth", "tiger", "crown",
        "dream", "heart", "storm", "cloud", "brave", "smile", "paper", "stone", "green",
        "black", "white", "quick", "piano", "candy", "magic", "queen", "river", "ocean",
        "beach", "sugar", "honey", "lemon", "grape", "peach", "angel", "ghost", "witch",
        "sword", "arrow", "flame", "crane", "eagle", "horse", "sheep", "snake", "tiger",
    ],
    6: [
        "planet", "orange", "flower", "silver", "yellow", "purple", "friend", "school",
        "sunset", "forest", "garden", "market", "castle", "palace", "window", "animal",
        "summer", "winter", "spring", "autumn", "pirate", "dragon", "singer", "travel",
        "rocket", "bridge", "island", "valley", "candle", "pencil", "guitar", "doctor",
        "artist", "writer", "dancer", "player", "hunter", "knight", "wizard", "secret",
    ],
}


# ═══════════════════════════════════════════════
# TRY TO LOAD wordfreq
# ═══════════════════════════════════════════════
_loaded = False

try:
    from wordfreq import top_n_list
    print("📚 Loading English word pool from wordfreq...")

    _TOP_WORDS = top_n_list('en', 50000)
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

    _loaded = True
    print(f"✅ wordfreq loaded: 4L={len(WORD_POOL[4])}, 5L={len(WORD_POOL[5])}, 6L={len(WORD_POOL[6])}")

except Exception as e:
    print(f"⚠️ wordfreq failed ({e}), using fallback word list.")
    for length in (4, 5, 6):
        WORD_POOL[length] = FALLBACK_WORDS[length]
    _loaded = False
    print(f"✅ Fallback loaded: 4L={len(WORD_POOL[4])}, 5L={len(WORD_POOL[5])}, 6L={len(WORD_POOL[6])}")


# ═══════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════
def get_random_word(length: int) -> str:
    """Return a random common English word of given length."""
    pool = WORD_POOL.get(length, [])
    if not pool:
        return {4: "star", 5: "apple", 6: "planet"}.get(length, "apple")
    return random.choice(pool)


def is_valid_word(word: str, length: int) -> bool:
    """Check if the guessed word is in our pool."""
    word = word.lower().strip()
    if len(word) != length or not word.isalpha():
        return False
    return word in WORD_POOL.get(length, [])


def words_count() -> dict:
    """Return count of words per length."""
    return {k: len(v) for k, v in WORD_POOL.items()}
