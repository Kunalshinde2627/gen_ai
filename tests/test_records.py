
import json

from app import records


def create_test_records(tmp_path, monkeypatch):
    data = [
        {
            "id": "R1",
            "topic": "Income Tax",
            "summary": "Tax on income earned by a person.",
            "source_url": "https://example.com/income",
            "regime": "both"
        },
        {
            "id": "R2",
            "topic": "Form 16",
            "summary": "Certificate issued by an employer.",
            "source_url": "https://example.com/form16",
            "regime": "old"
        }
    ]

    file_path = tmp_path / "records.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr(records, "DATA_FILE", file_path)

    return data


def test_load_records(tmp_path, monkeypatch):
    expected = create_test_records(tmp_path, monkeypatch)

    result = records.load_records()

    assert len(result) == 2
    assert result == expected


def test_get_record_by_id(tmp_path, monkeypatch):
    create_test_records(tmp_path, monkeypatch)

    result = records.get_record("R1")

    assert result["topic"] == "Income Tax"


def test_get_record_case_insensitive(tmp_path, monkeypatch):
    create_test_records(tmp_path, monkeypatch)

    result = records.get_record("r1")

    assert result is not None
    assert result["id"] == "R1"


def test_get_record_not_found(tmp_path, monkeypatch):
    create_test_records(tmp_path, monkeypatch)

    result = records.get_record("R99")

    assert result is None


def test_search_records(tmp_path, monkeypatch):
    create_test_records(tmp_path, monkeypatch)

    result = records.search_records("income")

    assert len(result) == 1
    assert result[0]["id"] == "R1"


def test_count_by_regime(tmp_path, monkeypatch):
    create_test_records(tmp_path, monkeypatch)

    result = records.count_by("regime")

    assert result == {"both": 1, "old": 1}
