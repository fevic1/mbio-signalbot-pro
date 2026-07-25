from pathlib import Path

from aios.storage.json_backend import JSONBackend


def test_storage_append_read(tmp_path):

    backend = JSONBackend(
        root=str(tmp_path)
    )


    backend.append(
        "decisions",
        {
            "test": True
        }
    )


    records = backend.read(
        "decisions"
    )


    assert records[-1]["test"] is True
