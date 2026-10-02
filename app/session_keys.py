"""Case-local UI state, isolated between caseworkers sharing a browser session."""

import json


def case_key(caseworker: str, case_id: str, field: str) -> str:
    """Identify one field of one caseworker's case without delimiter collisions.

    Sentinels may be reused by different caseworkers. A case ID alone must not
    carry another caseworker's timer, preliminary judgment or AI reveal state.
    """
    return "case:" + json.dumps((caseworker, case_id, field), separators=(",", ":"))
