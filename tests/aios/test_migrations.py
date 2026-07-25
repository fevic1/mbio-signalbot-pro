from aios.storage.migrations import MigrationManager


def test_legacy_list_migration():

    manager = MigrationManager()


    result = manager.migrate(
        [
            {
                "legacy": True
            }
        ]
    )


    assert result["schema_version"] == 1

    assert result["records"][0]["legacy"] is True
