# Source: S8 synthetic cashy sample

## Provenance

- User-referenced CSV located at `C:\Users\giaco\Downloads\S8.synthetic_cashy_sample.csv` on 2026-10-01.
- Preserved unchanged at [`raw/S8.synthetic_cashy_sample.csv`](../../raw/S8.synthetic_cashy_sample.csv).
- Size: 471,761 bytes.
- SHA-256 of both copies: `a9f009737a034c4756003a477365c5dbcdddb96562f329fd4c56c26281fe71c1`.
- Format: comma-separated table with a header, 1,900 data rows and 26 columns.
- The [[sources/cashy-oversight-challenge-site|challenge site]] links to the same CSV; the downloaded copy has the identical SHA-256. The [[sources/cashy-oversight-challenge-brief|brief]] explicitly names S8 as the released challenge dataset and supplies Annex I's dictionary and generation constraints.

## Scope of ingest

The full file is retained under `raw/`. In keeping with the user's request, the wiki records a [[topics/csv-mini-eda|mini EDA]] and macro-level measures only. It does not reproduce household-level records, run detailed modeling, or infer a causal relationship between variables.

## Limits

- There is no row identifier in the 26-column file. Exact duplicate rows cannot be classified as errors without more context.
- Codes such as `sotap` in `OficinaACNUR` are anonymized field-office labels; actual locations are not disclosed.
- The site and brief establish its relationship to the challenge, **not** that its frequencies represent real beneficiaries. Synthetic generation preserves the Scorecard's structure/value sets/arithmetic but not the true operation's distribution. See [[topics/cashy-data|dictionary and interpretation]].
