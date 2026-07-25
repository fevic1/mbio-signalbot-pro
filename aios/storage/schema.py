CURRENT_SCHEMA_VERSION = 1


def wrap(records):

    return {
        "schema_version":
            CURRENT_SCHEMA_VERSION,

        "records":
            records,
    }
