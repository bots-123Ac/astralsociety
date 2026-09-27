import random

# ═══════════════════════════════════════════════
# REAL ENGLISH DICTIONARY via wordfreq
# ═══════════════════════════════════════════════
WORD_POOL = set()

try:
    from wordfreq import top_n_list
    print("📚 Loading 5-letter English word pool...")

    # Top 100,000 most common English words
    _ALL_WORDS = top_n_list('en', 100000)

    for _w in _ALL_WORDS:
        _w = _w.lower().strip()
        if len(_w) == 5 and _w.isalpha() and _w.isascii():
            WORD_POOL.add(_w)

    print(f"✅ Loaded {len(WORD_POOL)} five-letter words")

except Exception as e:
    print(f"⚠️ wordfreq failed: {e}")
    print("⚠️ Using fallback minimal word list")
    # Fallback minimal list (only if wordfreq fails)
    WORD_POOL = {
        "apple", "house", "light", "water", "happy", "music", "earth", "tiger",
        "crown", "dream", "heart", "storm", "cloud", "brave", "smile", "paper",
        "stone", "green", "black", "white", "quick", "piano", "candy", "magic",
        "queen", "river", "ocean", "beach", "sugar", "honey", "lemon", "grape",
        "peach", "angel", "ghost", "witch", "sword", "arrow", "flame", "crane",
        "eagle", "horse", "sheep", "snake", "tower", "mount", "field", "point",
        "plant", "table", "chair", "board", "phone", "watch", "glass", "clock",
        "power", "laugh", "peace", "faith", "trust", "glory", "shine", "pride",
        "trend", "bloom", "fresh", "brisk", "swift", "smart", "proud", "young",
        "sweet", "plain", "grain", "brain", "train", "chain", "charm", "chart",
        "chase", "cheap", "check", "cheek", "cheer", "chess", "chest", "chief",
        "child", "choir", "chose", "civil", "claim", "class", "clean", "clear",
        "clerk", "click", "cliff", "climb", "cling", "close", "cloth", "coach",
        "coast", "count", "court", "cover", "crash", "cream", "crime", "cross",
        "crowd", "curve", "cycle", "daily", "dance", "death", "delay", "depth",
        "diary", "dirty", "doubt", "dozen", "draft", "drain", "drama", "drawn",
        "dress", "drift", "drill", "drink", "drive", "drove", "dying", "eager",
        "early", "eight", "elder", "empty", "enemy", "enjoy", "enter", "entry",
        "equal", "error", "event", "every", "exact", "exist", "extra", "false",
        "fault", "favor", "fence", "fewer", "fifth", "fifty", "fight", "final",
        "first", "fixed", "flash", "fleet", "floor", "flour", "fluid", "focus",
        "force", "forth", "forty", "forum", "found", "frame", "frank", "fraud",
        "front", "fruit", "fully", "funny", "giant", "given", "globe", "going",
        "grace", "grade", "grand", "grant", "grass", "grave", "great", "gross",
        "group", "grown", "guard", "guess", "guest", "guide", "heavy", "hence",
        "hotel", "human", "ideal", "image", "index", "inner", "input", "issue",
        "joint", "judge", "known", "label", "large", "laser", "later", "layer",
        "learn", "lease", "least", "leave", "legal", "level", "limit", "local",
        "logic", "loose", "lower", "lucky", "lunch", "lying", "major", "maker",
        "march", "match", "maybe", "mayor", "meant", "media", "metal", "might",
        "minor", "minus", "mixed", "model", "money", "month", "moral", "motor",
        "mouse", "mouth", "movie", "needs", "never", "newly", "night", "noise",
        "north", "noted", "novel", "nurse", "occur", "offer", "often", "order",
        "other", "ought", "paint", "panel", "party", "phase", "phone", "photo",
        "piece", "pilot", "pitch", "place", "plane", "plate", "pound", "press",
        "price", "prime", "print", "prior", "prize", "proof", "prove", "quiet",
        "quite", "radio", "raise", "range", "rapid", "ratio", "reach", "ready",
        "refer", "right", "rival", "river", "round", "route", "royal", "rural",
        "scale", "scene", "scope", "score", "sense", "serve", "seven", "shall",
        "shape", "share", "sharp", "sheet", "shelf", "shell", "shift", "shine",
        "shirt", "shock", "shoot", "short", "shown", "sight", "since", "sixth",
        "sixty", "sized", "skill", "sleep", "slide", "small", "smoke", "solid",
        "solve", "sorry", "sound", "south", "space", "spare", "speak", "speed",
        "spend", "spent", "split", "spoke", "sport", "staff", "stage", "stake",
        "stand", "start", "state", "steam", "steel", "stick", "still", "stock",
        "stood", "store", "story", "strip", "stuck", "study", "stuff", "style",
        "suite", "super", "taken", "taste", "taxes", "teach", "teeth", "thank",
        "theft", "their", "theme", "there", "these", "thick", "thing", "think",
        "third", "those", "three", "threw", "throw", "tight", "times", "tired",
        "title", "today", "topic", "total", "touch", "tough", "track", "trade",
        "treat", "trial", "tried", "tries", "truck", "truly", "truth", "twice",
        "under", "undue", "union", "unity", "until", "upper", "upset", "urban",
        "usage", "usual", "valid", "value", "video", "virus", "visit", "vital",
        "voice", "waste", "wheel", "where", "which", "while", "white", "whole",
        "whose", "woman", "women", "world", "worry", "worse", "worst", "worth",
        "would", "wound", "write", "wrong", "wrote", "young", "youth",
    }


def get_random_5letter_word() -> str:
    """Return a random common 5-letter English word."""
    if not WORD_POOL:
        return "apple"
    return random.choice(list(WORD_POOL))


def is_valid_word(word: str) -> bool:
    """Check if word is a valid 5-letter English word."""
    word = word.lower().strip()
    if len(word) != 5 or not word.isalpha() or not word.isascii():
        return False
    # Reject all-same-letter (aaaaa, xxxxx)
    if len(set(word)) == 1:
        return False
    return word in WORD_POOL
