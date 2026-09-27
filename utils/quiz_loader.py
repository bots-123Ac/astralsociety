import asyncio
import html as html_lib
import logging

import aiohttp

from utils.database import add_quiz_question, get_quiz_count

logger = logging.getLogger(__name__)

# opentdb category mapping
OPENTDB_CATEGORIES = {
    "general": 9,
    "movies": 11,
    "music": 12,
    "tech": 18,
    "maths": 19,
    "history": 23,
    "geography": 22,
    "sports": 21,
    "science": 17,
    "animals": 27,
    "politics": 24,
    "literature": 10,
    "food": 9,        # mapped to general
    "business": 9,    # mapped to general
    "space": 17,      # mapped to science
}

TARGET_COUNT = 5000
FETCH_ROUNDS = 30  # per category


async def _fetch_one_round(session, cat_name: str, cat_id: int):
    url = (
        f"https://opentdb.com/api.php"
        f"?amount=50&category={cat_id}&type=multiple"
    )
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                return 0
            data = await resp.json()
    except Exception as e:
        logger.warning(f"Fetch error {cat_name}: {e}")
        return 0

    results = data.get("results", [])
    if not results:
        return 0

    added = 0
    for q in results:
        try:
            question = html_lib.unescape(q["question"])
            correct = html_lib.unescape(q["correct_answer"])
            wrongs = [html_lib.unescape(x) for x in q["incorrect_answers"]]
            ok = await add_quiz_question(cat_name, question, correct, wrongs)
            if ok:
                added += 1
        except Exception as e:
            logger.warning(f"Save error: {e}")
            continue
    return added


async def fetch_all_questions():
    """Fetch from opentdb until TARGET_COUNT reached."""
    current = await get_quiz_count()
    if current >= TARGET_COUNT:
        logger.info(f"✅ Already have {current} questions. Skipping fetch.")
        return

    logger.info(f"📚 Current: {current}. Fetching more from opentdb...")

    async with aiohttp.ClientSession() as session:
        for round_num in range(FETCH_ROUNDS):
            for cat_name, cat_id in OPENTDB_CATEGORIES.items():
                count = await get_quiz_count()
                if count >= TARGET_COUNT:
                    logger.info(f"🎯 Target reached: {count} questions")
                    return
                added = await _fetch_one_round(session, cat_name, cat_id)
                if added > 0:
                    logger.info(
                        f"Round {round_num + 1} | {cat_name}: +{added} "
                        f"(total {await get_quiz_count()})"
                    )
                await asyncio.sleep(3)  # rate limit


async def background_load():
    """Run in background without blocking bot startup."""
    try:
        await fetch_all_questions()
    except Exception as e:
        logger.error(f"Background quiz load failed: {e}")
