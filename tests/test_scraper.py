from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import json
import requests

from src.data_collection.remoteok_api import RemoteOKClient, RemoteOKJob, fetch_to_json
from src.storage.json_repository import JobRecord, JSONJobStore

REMOTEOK_RESPONSE = [
    {"legal": "https://remoteok.com"},
    {
        "position": "Data Scientist",
        "description": "Analyze data and build predictive models.",
        "company": "DataWorks",
        "location": "Worldwide",
        "date": "2025-09-10",
        "tags": ["Data", "Python"],
        "url": "https://remoteok.com/remote-jobs/data-scientist",
    },
    {
        "position": "Frontend Engineer",
        "description": "Build modern web interfaces.",
        "company": "UI Labs",
        "location": "Remote",
        "date": "2025-09-01",
        "tags": ["JavaScript", "React"],
        "url": "https://remoteok.com/remote-jobs/frontend-engineer",
    },
]


class DummyResponse:
    def __init__(self, payload: List[dict], url: str) -> None:
        self._payload = payload
        self.url = url
        self.status_code = 200
        self.ok = True

    def raise_for_status(self) -> None:
        if not self.ok:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self) -> List[dict]:
        return self._payload


class DummySession:
    def __init__(self, payload: List[dict]) -> None:
        self.payload = payload
        self.calls: List[str] = []

    def get(self, url: str, timeout: int = 30):
        self.calls.append(url)
        return DummyResponse(self.payload, url)


def test_client_filters_by_tag_and_keyword(tmp_path):
    session = DummySession(REMOTEOK_RESPONSE)
    client = RemoteOKClient(session=session, output_path=tmp_path / "jobs.json")
    jobs = client.fetch_jobs(tags=["data"], keyword="models", persist=False)
    assert len(jobs) == 1
    assert jobs[0].job_title == "Data Scientist"
    assert session.calls == ["https://remoteok.com/api"]

def test_client_persists_to_json(tmp_path):
    session = DummySession(REMOTEOK_RESPONSE)
    output = tmp_path / "jobs.json"
    client = RemoteOKClient(session=session, output_path=output)
    jobs = client.fetch_jobs(persist=True)
    assert len(jobs) == 2
    contents = json.loads(output.read_text())
    assert contents[0]["job_title"] == "Data Scientist"

def test_fetch_to_json_helper(tmp_path, monkeypatch):
    class StubClient(RemoteOKClient):
        def __init__(self, *args, **kwargs):
            pass

        def fetch_jobs(self, **kwargs):
            return [RemoteOKJob("Test", "Desc", "Co", "Loc", "2025-09-10", [], "url")]

    monkeypatch.setattr("src.data_collection.remoteok_api.RemoteOKClient", StubClient)
    output = tmp_path / "jobs.json"
    count = fetch_to_json(output_path=output)
    assert count == 1
