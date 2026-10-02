# Local data

Download the released S8 synthetic CSV from the
[Cashy Oversight Challenge](https://maldonam.github.io/public/) and save it as:

```
data/S8.synthetic_cashy_sample.csv
```

Keep the file unchanged. Expected SHA-256:

```
a9f009737a034c4756003a477365c5dbcdddb96562f329fd4c56c26281fe71c1
```

The dataset, SQLite decision logs, simulations and exported tables are local
runtime inputs/outputs and must not be committed. The application resolves
their paths from the repository root. Field definitions and value translations
used by the application are in `src/data_dictionary.py`.

All cases are synthetic, not actual beneficiaries. The sample and its labels
do not establish real-world distributions or operational eligibility.
