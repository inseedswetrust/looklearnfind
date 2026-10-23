"""Contract-matching guards for the dark-horse monitor."""
import re


def polymarket_match_ok(question, candidate_name, state, race):
    """A Polymarket market is attached to a candidate only if the question names the candidate's surname AND the race.

    race is 'SEN' or 'HOUSE-14'. This is what rejected an NHL player and an NFL quarterback that share a surname with a candidate.
    """
    q = (question or "").lower()
    last = re.sub(r"[^a-z ]", "", candidate_name.lower()).split()[-1]
    if not re.search(rf"\b{re.escape(last)}\b", q):
        return False
    if race == "SEN":
        return "senate" in q and _state_name(state) in q
    m = re.match(r"HOUSE-(\d+)", race)
    if not m:
        return False
    n = int(m.group(1))
    return bool(re.search(rf"{state.lower()}[- ]?0?{n}\b", q) or re.search(rf"\b{n}(st|nd|rd|th) (congressional )?district", q)) and ("house" in q or "congress" in q)


_NAMES = {"CA": "california", "FL": "florida", "MI": "michigan", "IL": "illinois", "MN": "minnesota", "TX": "texas", "NY": "new york"}
def _state_name(s): return _NAMES.get(s, s.lower())
