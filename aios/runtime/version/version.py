from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeVersion:
    major: int = 1
    minor: int = 0
    patch: int = 0
    prerelease: str = ""
    build: str = ""

    @property
    def string(self):
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version

    def bump_major(self):
        self.major += 1
        self.minor = 0
        self.patch = 0

    def bump_minor(self):
        self.minor += 1
        self.patch = 0

    def bump_patch(self):
        self.patch += 1
