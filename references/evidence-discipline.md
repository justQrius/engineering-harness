# Evidence Discipline

Use this reference when a packet or review relies on proof artifacts rather
than prose alone.

## Goal

Move review from "trust me" to "prove it" by making evidence bundles explicit,
repeatable, and easy to validate.

## Recommended bundle shape

- one timestamped directory per validation run
- human-readable transcripts for the main path
- machine-readable payloads where possible
- optional `evidence-manifest.txt` when the bundle has a fixed expected set

## When to use a manifest

Use a manifest when:

- acceptance criteria name specific evidence artifacts
- review trust depends on the presence of a complete bundle
- the validation lane is expensive and you want mechanical completeness checks

## Validation rule

Run `python scripts/validate_evidence.py <bundle-dir>` before requesting review
when the packet depends on real-host or otherwise expensive evidence.