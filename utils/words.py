import random

# ═══════════════════════════════════════════════
# 5-LETTER COMMON ENGLISH WORD POOL
# ═══════════════════════════════════════════════
COMMON_5 = [
    "apple", "house", "light", "water", "happy", "music", "earth", "tiger", "crown",
    "dream", "heart", "storm", "cloud", "brave", "smile", "paper", "stone", "green",
    "black", "white", "quick", "piano", "candy", "magic", "queen", "river", "ocean",
    "beach", "sugar", "honey", "lemon", "grape", "peach", "angel", "ghost", "witch",
    "sword", "arrow", "flame", "crane", "eagle", "horse", "sheep", "snake", "tower",
    "mount", "field", "point", "plant", "table", "chair", "board", "phone", "watch",
    "glass", "clock", "power", "laugh", "peace", "faith", "trust", "glory", "shine",
    "pride", "trend", "bloom", "fresh", "brisk", "swift", "smart", "proud", "young",
    "sweet", "faint", "plain", "grain", "brain", "train", "chain", "charm", "chart",
    "chase", "cheap", "check", "cheek", "cheer", "chess", "chest", "chief", "child",
    "china", "choir", "chose", "civil", "claim", "class", "clean", "clear", "clerk",
    "click", "cliff", "climb", "cling", "close", "cloth", "coach", "coast", "count",
    "court", "cover", "crash", "cream", "crime", "cross", "crowd", "curve", "cycle",
    "daily", "dance", "death", "debug", "delay", "depth", "diary", "dirty", "doubt",
    "dozen", "draft", "drain", "drama", "drawn", "dress", "drift", "drill", "drink",
    "drive", "drove", "dying", "eager", "early", "eight", "elder", "empty", "enemy",
    "enjoy", "enter", "entry", "equal", "error", "event", "every", "exact", "exist",
    "extra", "false", "fault", "favor", "fence", "fewer", "fifth", "fifty", "fight",
    "final", "first", "fixed", "flash", "fleet", "floor", "flour", "fluid", "focus",
    "force", "forth", "forty", "forum", "found", "frame", "frank", "fraud", "front",
    "fruit", "fully", "funny", "giant", "given", "globe", "going", "grace", "grade",
    "grand", "grant", "grass", "grave", "great", "gross", "group", "grown", "guard",
    "guess", "guest", "guide", "harry", "heavy", "hence", "hotel", "human", "ideal",
    "image", "index", "inner", "input", "issue", "japan", "joint", "judge", "known",
    "label", "large", "laser", "later", "layer", "learn", "lease", "least", "leave",
    "legal", "level", "limit", "links", "lives", "local", "logic", "loose", "lower",
    "lucky", "lunch", "lying", "major", "maker", "march", "match", "maybe", "mayor",
    "meant", "media", "metal", "might", "minor", "minus", "mixed", "model", "money",
    "month", "moral", "motor", "mouse", "mouth", "movie", "needs", "never", "newly",
    "night", "noise", "north", "noted", "novel", "nurse", "occur", "offer", "often",
    "order", "other", "ought", "paint", "panel", "party", "peter", "phase", "photo",
    "piece", "pilot", "pitch", "place", "plane", "plate", "pound", "press", "price",
    "prime", "print", "prior", "prize", "proof", "prove", "quiet", "quite", "radio",
    "raise", "range", "rapid", "ratio", "reach", "ready", "refer", "right", "rival",
    "robin", "roger", "roman", "rough", "round", "route", "royal", "rural", "scale",
    "scene", "scope", "score", "sense", "serve", "seven", "shall", "shape", "share",
    "sharp", "sheet", "shelf", "shell", "shift", "shine", "shirt", "shock", "shoot",
    "short", "shown", "sight", "since", "sixth", "sixty", "sized", "skill", "sleep",
    "slide", "small", "smith", "smoke", "solid", "solve", "sorry", "sound", "south",
    "space", "spare", "speak", "speed", "spend", "spent", "split", "spoke", "sport",
    "staff", "stage", "stake", "stand", "start", "state", "steam", "steel", "stick",
    "still", "stock", "stood", "store", "story", "strip", "stuck", "study", "stuff",
    "style", "suite", "super", "taken", "taste", "taxes", "teach", "teeth", "terry",
    "texas", "thank", "theft", "their", "theme", "there", "these", "thick", "thing",
    "think", "third", "those", "three", "threw", "throw", "tight", "times", "tired",
    "title", "today", "topic", "total", "touch", "tough", "track", "trade", "treat",
    "trial", "tried", "tries", "truck", "truly", "truth", "twice", "under", "undue",
    "union", "unity", "until", "upper", "upset", "urban", "usage", "usual", "valid",
    "value", "video", "virus", "visit", "vital", "voice", "waste", "wheel", "where",
    "which", "while", "whole", "whose", "woman", "women", "world", "worry", "worse",
    "worst", "worth", "would", "wound", "write", "wrong", "wrote", "youth",
]

WORD_POOL = set(COMMON_5)


def get_random_5letter_word() -> str:
    return random.choice(list(WORD_POOL))


def is_valid_word(word: str) -> bool:
    word = word.lower().strip()
    if len(word) != 5 or not word.isalpha():
        return False
    # Reject all-same-letter words (like "aaaaa")
    if len(set(word)) == 1:
        return False
    return word in WORD_POOL
