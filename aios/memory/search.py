from pathlib import Path


class MemorySearch:

    def __init__(
        self,
        vault="docs/obsidian"
    ):
        self.vault = Path(vault)


    def search(
        self,
        query,
        folder=None
    ):

        if folder:
            location = self.vault / folder
        else:
            location = self.vault


        if not location.exists():
            return []


        results = []


        for file in location.rglob("*.md"):

            content = file.read_text(
                errors="ignore"
            )


            if query.lower() in content.lower():

                results.append(
                    {
                        "file": str(file),
                        "match": query
                    }
                )


        return results

