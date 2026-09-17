"""Thin wrapper around the Grist REST API."""

import requests
from django.conf import settings


class GristClient:
    def __init__(self, base_url=None, api_key=None, doc_id=None):
        self.base_url = (base_url or settings.GRIST_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.GRIST_API_KEY
        self.doc_id = doc_id or settings.GRIST_DOC_ID

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def _records_url(self, table, suffix=""):
        return f"{self.base_url}/api/docs/{self.doc_id}/tables/{table}/records{suffix}"

    def list_records(self, table):
        """Return every record of a table as [{"id": ..., "fields": {...}}, ...]."""
        response = requests.get(
            self._records_url(table), headers=self._headers(), timeout=10
        )
        response.raise_for_status()
        return response.json()["records"]

    def list_records_safe(self, table):
        """Return table records, or empty list [] if table does not exist."""
        try:
            return self.list_records(table)
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return []
            raise

    def create_records(self, table, records):
        """Create records. `records` is a list of {field: value} dicts."""
        payload = {"records": [{"fields": fields} for fields in records]}
        response = requests.post(
            self._records_url(table),
            json=payload,
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["records"]

    def update_records(self, table, records):
        """Update records. `records` is a list of {"id": ..., "fields": {...}}."""
        response = requests.patch(
            self._records_url(table),
            json={"records": records},
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()

    def delete_records(self, table, record_ids):
        response = requests.post(
            self._records_url(table, "/delete"),
            json=record_ids,
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()


client = GristClient()
