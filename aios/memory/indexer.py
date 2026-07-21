from pathlib import Path


class MemoryIndexer:

    def __init__(
        self,
        vault="docs/obsidian"
    ):
        self.vault = Path(vault)


    def create_link(
        self,
        source_file,
        target_name
    ):

        source = Path(source_file)

        if not source.exists():
            return False

        content = source.read_text()

        link = f"- [[{target_name}]]"

        if link in content:
            return True


        if "## Related" in content:

            content = content.replace(
                "## Related\n",
                "## Related\n\n" + link + "\n",
                1
            )

        else:

            content += (
                "\n\n## Related\n\n"
                + link
                + "\n"
            )


        source.write_text(content)

        return True


    def list_memory(
        self,
        memory_type=None
    ):

        if memory_type:
            folder = self.vault / memory_type
        else:
            folder = self.vault


        if not folder.exists():
            return []


        return [
            str(file)
            for file in folder.rglob("*.md")
        ]
