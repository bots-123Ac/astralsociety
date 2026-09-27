import random

# 5-letter word pool (common English)
WORDS_5 = [
    "apple", "house", "light", "water", "happy", "music", "earth", "tiger", "crown",
    "dream", "heart", "storm", "cloud", "brave", "smile", "paper", "stone", "green",
    "black", "white", "quick", "piano", "candy", "magic", "queen", "river", "ocean",
    "beach", "sugar", "honey", "lemon", "grape", "peach", "angel", "ghost", "witch",
    "sword", "arrow", "flame", "crane", "eagle", "horse", "sheep", "snake", "tiger",
    "tower", "mount", "field", "point", "plant", "table", "chair", "board", "phone",
    "watch", "glass", "clock", "stone", "cloud", "dream", "power", "smile", "laugh",
    "peace", "faith", "trust", "glory", "shine", "pride", "crown", "trend", "bloom",
    "fresh", "brisk", "swift", "smart", "proud", "young", "sweet", "brave", "faint",
]


def get_random_5letter_word() -> str:
    return random.choice(WORDS_5)
