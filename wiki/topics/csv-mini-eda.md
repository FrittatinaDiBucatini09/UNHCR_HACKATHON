# CSV mini EDA: S8 synthetic cashy sample

## Coverage

| Measure | Aggregate |
|---|---:|
| Data rows | 1,900 |
| Columns | 26 |
| Months represented | 14, from 2023-06 through 2024-07 |
| Exact duplicate rows | 14 (0.7%) |
| `NumIntegrantes`, median | 2; range 1–11 |
| `FinalScore`, median | 27.09; interquartile range 16.56–37.91; range 0–81.13 |

The monthly row count ranges from 30 (2024-07) to 187 (2024-05). These counts describe this file, not the size or trend of a real population.

## Main labels

| Field | Values in this file |
|---|---|
| `EligibilityTarget` | `INCLUSION`: 427 (22.5%); `EXCLUSION`: 1,473 (77.5%) |
| `Elegibilidad` | `No Elegible`: 932; `Lista de Reserva`: 451; `Elegible`: 414; `No Elegible por Intenciones`: 52; `No Elegible por Duplicidad`: 38; `Elegible por Proceso Acelerado`: 13 |
| `Vulnerability_Category` | `Vulnerabilidad Baja`: 775; `Vulnerabilidad Elevada`: 612; `Vulnerabilidad Moderada`: 394; `Vulnerabilidad Severa`: 119 |

In this file, all 427 `INCLUSION` rows have `Elegibilidad` equal to `Elegible` or `Elegible por Proceso Acelerado`; all other `Elegibilidad` values map to `EXCLUSION`. The [[sources/cashy-oversight-challenge-brief|challenge brief]] explicitly defines this deterministic mapping for S8. The two columns are therefore not independent evidence and must not be used as predictors of one another.

## Completeness

- `ScoreCOMAR_PIL`: 960 missing (50.5%).
- `FemaleHeadedHousehold`: 925 missing (48.7%).
- `CuidadorSolo`: 925 missing (48.7%).
- `OficinaACNUR`: 21 missing (1.1%).
- The remaining 22 columns have no missing values in this file.

`OficinaACNUR` contains seven non-null anonymized office codes. `sotap` appears in 1,278 rows (67.3%), the largest code group. The challenge dictionary identifies the codes as offices but does not disclose actual office names.

## Interpretation boundary

The [[sources/cashy-oversight-challenge-site|site]] and [[sources/cashy-oversight-challenge-brief|brief]] establish this as the challenge's released S8 synthetic sample; the website download has the same SHA-256 as the local CSV. One row represents a synthetic household interview. The source says generation preserves structure, variable values and score arithmetic, **not** the operation's actual distribution. The counts above are descriptive properties of S8, not real beneficiary statistics. There is no row ID, so the 14 exact duplicates are an observation, not a confirmed defect. The dataset's score/category structure makes it unsuitable for benchmarking real-world eligibility accuracy; see [[topics/cashy-data|data boundaries]].

## Source

[[sources/s8-synthetic-cashy-sample|S8 synthetic cashy sample]]; unchanged raw data: [`raw/S8.synthetic_cashy_sample.csv`](../../raw/S8.synthetic_cashy_sample.csv).
