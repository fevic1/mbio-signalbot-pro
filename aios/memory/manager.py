from .obsidian import ObsidianWriter
from .validator import MemoryValidator


class MemoryManager:

    def __init__(self):

        self.writer = ObsidianWriter()
        self.validator = MemoryValidator()


    def remember(
        self,
        memory_type,
        title,
        content,
        metadata=None
    ):

        valid = self.validator.validate(
            memory_type,
            content
        )


        if not valid:
            raise ValueError(
                "Memory rejected by validator"
            )


        return self.writer.write_memory(
            memory_type=memory_type,
            title=title,
            content=content,
            metadata=metadata
        )
