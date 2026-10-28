# Changelog

## 0.1.0 (vinf-luj)

### BREAKING: compress uses JSON, not pickle

- `compressDict` encodes with JSON by default (was `pickle.dumps`). Data that JSON
  cannot hold (`Decimal`, `datetime`, `bytes`, `set`, tuples come back as lists)
  now raises `TypeError`; convert it first (for example `nicHelper.dictUtil.filterDt`
  for datetimes) or pass your own `encoder`/`decoder` pair.
- `decompressDict` decodes with JSON by default (was `pickle.loads`). A blob made by
  0.0.120 or older with the old default starts with the pickle header `0x80` after
  decompression; `decompressDict` raises `ValueError` for it and never unpickles it.
  There is no pickle fallback: unpickling data you are handed can run code.

Migrating a stored blob (an env var, a DynamoDB field, a file):

1. Decode it once, offline, from a source you trust (your own template or table),
   with an unpickler that only allows plain types, then re-encode it with
   `compressDict` from 0.1.0.
2. Ship the new blob together with code that decodes it explicitly:
   `decompressDict(blob, decoder=json.loads)` works with every nicHelper version,
   so the consumer does not depend on which layer version it gets.
3. Only then move the consumer to a layer with nicHelper 0.1.0. If you cannot
   migrate yet, pin `nicHelper<=0.0.120` in that consumer.

### Other hardening

- `SuperModel` reads a vendored copy of the squirrel OpenAPI schema
  (`nicHelper/schemas`); importing `nicHelper.pynamodb` no longer fetches a gist.
- Every yaml load is `safe_load`/`SafeLoader`: files with `!!python/...` tags are refused.
- `githubImportModule` raises `NotImplementedError` instead of downloading and running Python.
- `getDistanceOsrm` defaults to `https://router.project-osrm.org`.
- `schema.readSchemaText` and `schema.squirrelSchemaPath` are new.
