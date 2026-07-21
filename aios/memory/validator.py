class MemoryValidator:

    ALLOWED_TYPES = [
        "session",
        "research",
        "decision",
        "project",
        "lesson",
        "incident",
        "review",
        "trading",
        "agent",
        "task"
    ]


    def validate(
        self,
        memory_type,
        content
    ):

        if not memory_type:
            return False


        if memory_type not in self.ALLOWED_TYPES:
            return False


        if not content:
            return False


        if len(content.strip()) < 10:
            return False


        return True
