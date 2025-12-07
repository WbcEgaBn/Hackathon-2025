import json
import re
from collections import defaultdict
from pathlib import Path


RULEBOOK_PATH = Path(__file__).parent / "rulebook" / "topics.json"

RULES = {}
THRESHOLD_RATIO = 0.5

if RULEBOOK_PATH.exists():
    with open(RULEBOOK_PATH, "r", encoding="utf-8") as f:
        rb = json.load(f)
    RULES = rb.get("topics", {})
    THRESHOLD_RATIO = rb.get("threshold_ratio", 0.5)


def _get_field(item, field_name):
    if isinstance(item, dict):
        return item.get(field_name)
    return getattr(item, field_name, None)


def classify_topics(item):

    title = (_get_field(item, "item_title") or "").lower()
    desc = (_get_field(item, "description") or "").lower()
    raw  = (_get_field(item, "raw_block") or "").lower()
    case = (_get_field(item, "case_code") or "")

    text = " ".join([title, desc, raw]).lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)

    case_upper = case.upper()

    scores = defaultdict(int)

    for topic, rule in RULES.items():
        for prefix in rule.get("case_prefixes", []):
            if case_upper.startswith(prefix):
                scores[topic] += rule.get("weight_case", 5)

        for kw in rule.get("keywords", []):
            kw = kw.lower()
            if kw and kw in text:
                scores[topic] += rule.get("weight_keyword", 3)

    topics_from_rulebook = set()

    if scores:
        max_score = max(scores.values())
        threshold = max_score * THRESHOLD_RATIO
        for topic, score in scores.items():
            if score >= threshold:
                topics_from_rulebook.add(topic)

    fallback_topics = set()

    if case_upper.startswith(("ZONE", "ZON", "ZC", "REZ", "MAP")):
        fallback_topics.add("zoning")

    zoning_terms = [
        "zone map", "rezone", "rezoning", "pdz", "pud",
        "planned development", "development plan",
    ]
    if any(term in text for term in zoning_terms):
        fallback_topics.add("zoning")

    # --- CONDITIONAL USE ---------------------------------------
    if case_upper.startswith(("CUDP", "CU", "CONDU", "COND")):
        fallback_topics.add("conditional_use")
    if "conditional use" in text:
        fallback_topics.add("conditional_use")

    if any(word in text for word in ["marijuana", "cannabis", "retail marijuana"]):
        fallback_topics.add("marijuana_regulation")

    if any(term in text for term in ["school district", "high school", "elementary", "education"]):
        fallback_topics.add("education_facilities")

    if any(term in text for term in ["traffic", "parking", "roadway", "transportation"]):
        fallback_topics.add("infrastructure")

    if any(term in text for term in ["vacation", "right of way", "right-of-way"]):
        fallback_topics.add("right_of_way")

    if "urban renewal" in text:
        fallback_topics.add("urban_renewal")

    if any(term in text for term in ["dwelling units", "residential", "apartments", "housing"]):
        fallback_topics.add("residential_development")

    if any(term in text for term in ["commercial", "retail", "industrial", "office"]):
        fallback_topics.add("commercial_development")

    combined = list(dict.fromkeys(list(topics_from_rulebook) + list(fallback_topics)))

    return combined
