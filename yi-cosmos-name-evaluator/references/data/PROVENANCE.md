# Data provenance

`unihan-17.0.0.json.gz` is a deterministic extract of Unicode 17.0.0 `Unihan.zip` from:

- `https://www.unicode.org/Public/17.0.0/ucd/Unihan.zip`
- Properties: `kTotalStrokes`, `kTraditionalVariant`, `kSimplifiedVariant`, `kDefinition`, and `kMandarin`.

The source archive SHA-256 is embedded in the generated file metadata. Regenerate it with `scripts/build_unihan_data.py`; runtime evaluation never downloads data.

Unihan values are used as a reproducible default glyph-data convention. They are not represented as a unique or authoritative Kangxi naming-school stroke system. Explicit, sourced overrides take precedence and remain visible in the report.

Unicode data is redistributed under `UNICODE-LICENSE.txt`.

`numerology-81.json`, `trigrams.json`, and `hexagrams.json` are project-authored model configuration. Their interpretations are traditional-rule modeling choices rather than empirical or scientific claims.
