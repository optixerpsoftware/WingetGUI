from src.winget.models import WingetPackage

# Colonnes connues qui peuvent apparaître entre Version et Source.
_KNOWN_MIDDLE_COLUMNS = ("Match", "Available")


def parse_search_output(output: str) -> list[WingetPackage]:
    """Parse la sortie tabulaire de `winget search` ou `winget list`.

    Winget utilise des colonnes à largeur fixe. On déduit les positions
    depuis la ligne d'en-tête, puis on découpe chaque ligne par index.
    Les colonnes intermédiaires (Match, Available) sont ignorées : seul
    `Version` est conservé.
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
    col_source  = header.index("Source") if "Source" in header else None

    # Borne supérieure de la colonne Version : la 1re colonne intermédiaire
    # connue (Match ou Available) si présente, sinon Source.
    middle_positions = [
        header.index(kw) for kw in _KNOWN_MIDDLE_COLUMNS if kw in header
    ]
    col_version_end = min(middle_positions) if middle_positions else col_source

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
