from src.winget.models import WingetPackage


def parse_search_output(output: str) -> list[WingetPackage]:
    """Parse la sortie tabulaire de `winget search`.

    Winget utilise des colonnes à largeur fixe. On déduit les positions
    depuis la ligne d'en-tête, puis on découpe chaque ligne par index.
    """
    lines = output.splitlines()

    header_index = next(
        (i for i, line in enumerate(lines) if "Name" in line and "Id" in line),
        None,
    )
    if header_index is None:
        return []

    header = lines[header_index]
    col_name    = header.index("Name")
    col_id      = header.index("Id")
    col_version = header.index("Version")
    col_match   = header.index("Match") if "Match" in header else None
    col_source  = header.index("Source") if "Source" in header else None

    # Borne supérieure de Version : Match si présente, sinon Source
    col_version_end = col_match or col_source

    data_lines = [
        line for line in lines[header_index + 1:]
        if line.strip() and not line.startswith("-")
    ]

    packages: list[WingetPackage] = []
    for line in data_lines:
        if len(line) < col_version:
            continue

        name    = line[col_name:col_id].strip()
        id_     = line[col_id:col_version].strip()
        version = (
            line[col_version:col_version_end].strip()
            if col_version_end else line[col_version:].strip()
        )
        source = line[col_source:].strip() if col_source else ""

        if name and id_:
            packages.append(WingetPackage(name=name, id=id_, version=version, source=source))

    return packages
