from dataclasses import dataclass


@dataclass(frozen=True)
class WingetPackage:
    name: str
    id: str
    version: str
    source: str

    def __str__(self) -> str:
        return f"{self.name} ({self.id}) — v{self.version} [{self.source}]"
