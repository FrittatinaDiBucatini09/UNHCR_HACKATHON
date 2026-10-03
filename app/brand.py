"""UNHCR logo files and the notice shown beside them.

The logos are the UNHCR insignia from Wikimedia Commons (File:UNHCR.svg and
File:UNHCR logo only (cropped).svg), unmodified. Every view that shows them
also says where the prototype comes from.
"""

from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"
LOGO = ASSETS / "unhcr_logo.svg"
EMBLEM = ASSETS / "unhcr_emblem.svg"
NOTICE = (
    "Sentinella: prototype for the Cashy Oversight Challenge, built at a "
    "University of Trento hackathon supported by UNHCR, on synthetic data."
)
