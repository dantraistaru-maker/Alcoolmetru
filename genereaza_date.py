#!/usr/bin/env python3
"""Scrie date.js din foaia 'Tabel extins' a fisierului Excel.

Ruleaza-l din nou daca tabelul se schimba:
    python genereaza_date.py ../Tabel_corectie_alcoolmetru.xlsx
"""
from __future__ import annotations

import json
import sys

from openpyxl import load_workbook

FOAIE = "Tabel extins"
CAP = 6  # randul cu concentratiile


def main() -> None:
    sursa = sys.argv[1] if len(sys.argv) > 1 else "../Tabel_corectie_alcoolmetru.xlsx"
    ws = load_workbook(sursa, data_only=True)[FOAIE]

    vols = []
    j = 2
    while (v := ws.cell(row=CAP, column=j).value) is not None:
        vols.append(int(v))
        j += 1
    temps, valori = [], []
    i = CAP + 1
    while (t := ws.cell(row=i, column=1).value) is not None:
        temps.append(int(t))
        valori.append([round(float(ws.cell(row=i, column=2 + k).value), 1)
                       for k in range(len(vols))])
        i += 1

    lipsa = [(temps[a], vols[b]) for a, r in enumerate(valori)
             for b, v in enumerate(r) if v is None]
    if lipsa:
        sys.exit(f"EROARE: valori lipsa in tabel: {lipsa[:5]}")

    # randurile sub domeniul masurat sunt calculate, nu citite din tabelul tiparit
    masurat_de_la = 10
    js = (
        "// Generat de genereaza_date.py - nu edita de mana.\n"
        "// Linii = temperatura distilatului (C), coloane = taria aparenta citita (% vol),\n"
        "// valori = taria reala la 20 C.\n"
        "export const TABEL = {\n"
        f"  temperaturi: {json.dumps(temps)},\n"
        f"  concentratii: {json.dumps(vols)},\n"
        f"  masuratDeLa: {masurat_de_la},\n"
        "  valori: [\n"
        + "".join(f"    {json.dumps(r)},\n" for r in valori)
        + "  ],\n};\n"
    )
    with open("date.js", "w", encoding="utf-8") as f:
        f.write(js)
    print(f"scris date.js: {len(temps)} temperaturi ({temps[0]}-{temps[-1]} C) x "
          f"{len(vols)} concentratii ({vols[0]}-{vols[-1]} % vol)")


if __name__ == "__main__":
    main()
