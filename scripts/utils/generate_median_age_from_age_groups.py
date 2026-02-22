#!/usr/bin/env python3
"""Génère un fichier Data/IRC/median_age.csv à partir des tranches d'âge (Data/Age)."""

from pathlib import Path
import csv
import re

AGE_DIR = Path(__file__).parent.parent / "Data" / "Age"
OUTPUT_FILE = Path(__file__).parent.parent / "Data" / "IRC" / "median_age.csv"

GROUP_ORDER = [
    (0, 4, "0004"),
    (5, 9, "0509"),
    (10, 14, "1014"),
    (15, 19, "1519"),
    (20, 24, "2024"),
    (25, 29, "2529"),
    (30, 34, "3034"),
    (35, 39, "3539"),
    (40, 44, "4044"),
    (45, 49, "4549"),
    (50, 54, "5054"),
    (55, 59, "5559"),
    (60, 64, "6064"),
    (65, 69, "65UP"),  # approximation pour la dernière tranche
]

GROUP_INDEX = {code: (lo, hi) for lo, hi, code in GROUP_ORDER}


def _find_header_row(rows):
    for i, row in enumerate(rows):
        if row and row[0].strip() == "Country Name":
            return i, row
    return None, None


def _load_group_file(file_path):
    """Charge un fichier de tranche d'âge et retourne un dict {(country_code, year): value} + noms pays."""
    data = {}
    country_names = {}

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    header_idx, header = _find_header_row(rows)
    if header_idx is None:
        return data, country_names

    year_cols = []
    for idx, col in enumerate(header):
        if re.fullmatch(r"\d{4}", col.strip()):
            year_cols.append((idx, col.strip()))

    for row in rows[header_idx + 1 :]:
        if not row or len(row) < 4:
            continue
        country_name = row[0].strip().strip("\"")
        country_code = row[1].strip().strip("\"")
        if not country_code:
            continue
        country_names[country_code] = country_name
        for idx, year in year_cols:
            if idx >= len(row):
                continue
            val = row[idx].strip().strip("\"")
            if val == "":
                continue
            try:
                data[(country_code, year)] = float(val)
            except ValueError:
                continue

    return data, country_names


def _collect_group_data():
    """Charge tous les fichiers FE/MA et retourne un dict {group_code: {sex: data}}"""
    group_data = {}
    country_names = {}

    for file_path in AGE_DIR.glob("POP.*.FE.csv"):
        match = re.search(r"POP\.(\w+)\.FE\.csv", file_path.name)
        if not match:
            continue
        group_code = match.group(1)
        if group_code not in GROUP_INDEX:
            continue
        data, names = _load_group_file(file_path)
        group_data.setdefault(group_code, {})["FE"] = data
        country_names.update(names)

    for file_path in AGE_DIR.glob("POP.*.MA.csv"):
        match = re.search(r"POP\.(\w+)\.MA\.csv", file_path.name)
        if not match:
            continue
        group_code = match.group(1)
        if group_code not in GROUP_INDEX:
            continue
        data, names = _load_group_file(file_path)
        group_data.setdefault(group_code, {})["MA"] = data
        country_names.update(names)

    return group_data, country_names


def _get_group_percent(group_data, country_code, year):
    """Retourne le % de population totale pour une tranche et une année.

    Les fichiers sont en % de la population féminine ou masculine. On approxime
    la population totale en moyenne simple (FE + MA) / 2 si les deux sont disponibles.
    """
    fe = group_data.get("FE", {}).get((country_code, year))
    ma = group_data.get("MA", {}).get((country_code, year))
    if fe is not None and ma is not None:
        return (fe + ma) / 2.0
    if fe is not None:
        return fe
    if ma is not None:
        return ma
    return None


def _compute_median_age(group_data, country_code, year):
    """Calcule l'âge médian par interpolation sur la tranche où le cumul passe 50%."""
    cumulative = 0.0
    for lo, hi, code in GROUP_ORDER:
        pct = _get_group_percent(group_data.get(code, {}), country_code, year)
        if pct is None:
            return None
        width = (hi - lo + 1) if code != "65UP" else 5
        if cumulative + pct >= 50.0:
            # interpolation linéaire dans la tranche
            if pct == 0:
                return None
            within = (50.0 - cumulative) / pct
            return lo + within * width
        cumulative += pct
    return None


def main():
    group_data, country_names = _collect_group_data()

    # Collecte des années disponibles
    years = set()
    for group in group_data.values():
        for sex_data in group.values():
            years.update(year for (_, year) in sex_data.keys())
    years = sorted(years)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "country_code",
            "country_name",
            "indicator_code",
            "indicator_name",
            "year",
            "value",
            "unit",
            "decimal",
        ])

        for country_code, country_name in sorted(country_names.items()):
            for year in years:
                median_age = _compute_median_age(group_data, country_code, year)
                if median_age is None:
                    continue
                writer.writerow([
                    country_code,
                    country_name,
                    "MEDIAN_AGE_CALC",
                    "Median age (calculated from 5-year age groups)",
                    year,
                    f"{median_age:.2f}",
                    "years",
                    "2",
                ])

    print(f"✅ Fichier généré : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
