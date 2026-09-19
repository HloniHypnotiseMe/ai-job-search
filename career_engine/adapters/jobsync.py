"""JobSync boundary adapter.

JobSync remains the candidate workspace/tracker. Until a stable external API
contract is pinned, this adapter uses a neutral JSON interchange format rather
than guessing private routes or database internals.
"""
from __future__ import annotations

import json
from typing import Any


class JobSyncAdapter:
    def __init__(self, export_path: str | None = None):
        self.export_path = export_path

    def import_snapshot(self, path: str | None = None) -> dict[str, Any]:
        target = path or self.export_path
        if not target:
            raise ValueError("A JobSync export path is required")
        with open(target, encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError("JobSync snapshot must be a JSON object")
        return payload

    @staticmethod
    def application_records(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        records = snapshot.get("applications", [])
        if not isinstance(records, list):
            raise ValueError("JobSync applications must be a list")
        return [record for record in records if isinstance(record, dict)]
