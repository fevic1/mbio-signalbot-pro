from dataclasses import dataclass, field


@dataclass
class ArchitectureReport:

    duplicate_symbols: dict = field(
        default_factory=dict
    )

    imports: dict = field(
        default_factory=dict
    )

    ownership_issues: list = field(
        default_factory=list
    )


    def to_dict(self):

        return {
            "duplicate_symbols":
                self.duplicate_symbols,

            "imports":
                self.imports,

            "ownership_issues":
                self.ownership_issues,
        }


    def healthy(self):

        return len(
            self.ownership_issues
        ) == 0
