from pathlib import Path
from datetime import datetime


class ObsidianWriter:

    ROUTES = {
        "session": "Sessions",
        "project": "Projects",
        "research": "Research",
        "decision": "Decisions",
        "agent": "Agents",
        "task": "Tasks",
        "incident": "Incidents",
        "review": "Reviews",
        "trading": "Trading",
        "daily": "Daily",
        "lesson": "Lessons",
        "skill": "Skills",
    }


    def __init__(
        self,
        vault="docs/obsidian"
    ):
        self.vault = Path(vault)

        self.vault.mkdir(
            parents=True,
            exist_ok=True
        )

    def write_memory(
        self,
        memory_type,
        title,
        content,
        metadata=None
    ):

        folder_name = self.ROUTES.get(
            memory_type,
            "Inbox"
        )

        folder = self.vault / folder_name

        folder.mkdir(
            parents=True,
            exist_ok=True
        )


        timestamp = datetime.utcnow()

        filename = (
            timestamp.strftime("%Y-%m-%d-%H%M%S")
            + ".md"
        )


        file = folder / filename


        meta = ""

        if metadata:
            meta = "\n".join(
                [
                    f"{key}: {value}"
                    for key, value in metadata.items()
                ]
            )


        file.write_text(
f"""---
type: {memory_type}
created: {timestamp.isoformat()}
{meta}
---

# {title}


## Content

{content}


## Related

- [[Home]]
"""
        )


        return str(file)



    def write_session(
        self,
        title,
        content
    ):

        return self.write_memory(
            memory_type="session",
            title=title,
            content=content
        )
