# Career discovery ingestion

The Career Command Centre uses **JobOps as a discovery/search adapter** rather than copying JobOps internals into the career engine.

## Contract

Input is a JSON export accepted by the existing JobOps adapter:

- a JSON list of job records, or
- an object containing a `jobs` list.

The importer:

1. normalizes each record;
2. preserves source URL/source identity;
3. records adapter provenance;
4. writes into the private CareerStore;
5. deduplicates on canonical key or source URL;
6. never auto-applies.

## Run

From the repository root:

```bash
python -m career_engine.discovery path/to/jobops-export.json --data-dir /private/career-data
```

The command prints counts for records seen, imported, and skipped as duplicates.

## Architecture boundary

This deliberately does **not** guess a JobOps HTTP API, database schema, or internal route. A stable external integration can be added later when one is verified.

This also means the Career Command Centre remains usable if discovery is supplied by another C6 Arsenal source in the future.
