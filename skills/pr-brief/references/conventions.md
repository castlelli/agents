# Conventions and signals to check against the diff

Report an item only when the diff touches it, quoting the lines. These are things a reviewer in bioinformatics wants to know changed; whether the change is right is theirs to decide.

## Domain conventions

- **Coordinates:** 0-based vs 1-based starts; anything that adds or subtracts 1 near `start`, `end`, `pos`, `offset`, slicing of sequences (`seq[s-1:e]`), `range(...)` bounds.
- **Interval ends:** inclusive vs exclusive; length computed as `end - start` vs `end - start + 1`; overlap tests using `<` vs `<=`.
- **Strand and orientation:** `+`/`-`, `1`/`-1`, reverse-complement, upstream/downstream when strand is negative, sort order within a strand.
- **Missing values:** NaN vs None vs empty string vs `-` vs 0; `dropna`, `fillna`, `astype(int)` on columns that can be missing; what is written to output files for missing values.
- **Identifiers:** accession versions (`WP_000001.1` vs `WP_000001`), taxonomy IDs (int vs str), GI numbers, assembly vs nucleotide vs protein ids, case changes.
- **Taxonomy:** lineage order, rank names, how unknown or merged taxids are handled.
- **Scores and thresholds:** e-value, bit score, coverage, identity cutoffs; their defaults; `<` vs `<=` at the cutoff.
- **Sort order and determinism:** sorts added or removed, `sort=False` in groupby, stable vs unstable sorts, ties, set/dict iteration order reaching output.
- **Output shape:** columns added, removed, renamed or reordered; dtypes; header lines; separators; file format (TSV, FASTA, GFF, BLAST tabular) changes; index written or not.
- **Defaults and signatures:** changed default arguments, removed or renamed parameters, new required parameters, CLI options added/removed/renamed in `bin/`.
- **Errors:** raising where it used to return a value (or the reverse), warnings removed, silent fallbacks added.
- **Dependencies:** changes to `requirements.txt` or `setup.py`; minimum versions (e.g. pandas 3 behaviour differences); new external tools called via subprocess.
- **Deprecation:** shims added or removed; deprecated paths still referenced by `bin/` or docs.

## Runtime alert signals

Raise "⚠ Runtime could change substantially" when the diff shows any of these on code that runs over whole tables, genomes or result files. Quote the lines and name the data the code runs on.

- Vectorised pandas/numpy code replaced by Python loops, `iterrows`, `apply(axis=1)`, or per-group `apply` (or the reverse: a large speed-up the PR doesn't mention).
- New nested loops over rows, blocks, genomes or hits; new self-joins or cross merges on large tables.
- Per-item file reads, subprocess calls or network requests inside a loop.
- Whole-file loading (`read()`, `readlines()`, full `read_csv`) where the code used to stream or chunk.
- Removed caching, memoisation, indexes, or `sort_index`/`set_index` that lookups relied on.
- A different algorithm on a hot path (e.g. interval overlap, clustering, alignment parsing).
- New `copy()` of large frames inside loops; repeated `pd.concat` in a loop.
