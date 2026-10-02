"""UNHCR logo files and the notice shown beside them.

The logos are the UNHCR insignia from Wikimedia Commons (File:UNHCR.svg and
File:UNHCR logo only (cropped).svg), unmodified. Insignia may not suggest an
endorsement, so every view that shows them also says the app is unofficial.
"""

from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"
LOGO = ASSETS / "unhcr_logo.svg"
EMBLEM = ASSETS / "unhcr_emblem.svg"
NOTICE = (
    "Sentinella: unofficial hackathon prototype for the UNHCR Cashy Oversight "
    "Challenge, on synthetic data. Not a UNHCR service."
)
