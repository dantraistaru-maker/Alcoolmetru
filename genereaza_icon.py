#!/usr/bin/env python3
"""Deseneaza iconul aplicatiei: un pahar cu alcoolmetrul plutind in el.

Desenul se face la rezolutie mare si se micsoreaza la final, ca marginile sa
iasa netede. Ruleaza:  python genereaza_icon.py
"""
from __future__ import annotations

from PIL import Image, ImageDraw

SS = 4  # supraesantionare


def gradient(size, sus, jos):
    img = Image.new("RGB", (1, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        k = y / max(1, size - 1)
        d.point((0, y), tuple(round(a + (b - a) * k) for a, b in zip(sus, jos)))
    return img.resize((size, size))


def masca_rotunjita(size, raza):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], raza, fill=255)
    return m


def deseneaza(S: int, zoom: float = 1.0, fundal_rotunjit: bool = True) -> Image.Image:
    s = S * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))

    fundal = gradient(s, (34, 49, 64), (16, 23, 32)).convert("RGBA")
    if fundal_rotunjit:
        fundal.putalpha(masca_rotunjita(s, int(0.235 * s)))
    img.alpha_composite(fundal)

    # tot desenul intr-un strat separat, ca sa-l pot scala pentru varianta mascabila
    strat = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(strat)
    c = s / 2

    # paharul: trunchi de con, usor mai ingust la baza
    sus_y, jos_y = 0.215 * s, 0.815 * s
    sus_w, jos_w = 0.215 * s, 0.170 * s
    gros = 0.034 * s
    interior = [(c - sus_w + gros, sus_y + gros), (c + sus_w - gros, sus_y + gros),
                (c + jos_w - gros, jos_y - gros), (c - jos_w + gros, jos_y - gros)]

    # lichidul, decupat pe forma interioara a paharului
    nivel = 0.415 * s
    lich = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(lich).polygon(interior, fill=(255, 255, 255, 255))
    culoare = gradient(s, (255, 197, 79), (223, 126, 24)).convert("RGBA")
    taiat = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    taiat.paste(culoare, (0, 0), lich)
    sub_nivel = Image.new("L", (s, s), 0)
    ImageDraw.Draw(sub_nivel).rectangle([0, nivel, s, s], fill=255)
    taiat.putalpha(Image.composite(taiat.getchannel("A"), Image.new("L", (s, s), 0), sub_nivel))
    strat.alpha_composite(taiat)

    # suprafata lichidului, o dunga mai deschisa
    lat = sus_w - gros - (sus_w - jos_w) * (nivel - sus_y) / (jos_y - sus_y)
    d.rectangle([c - lat, nivel - 0.012 * s, c + lat, nivel + 0.012 * s],
                fill=(255, 226, 150, 255))

    # Termo-alcoolmetrul, pe stratul lui, ca sa-l pot inclina. Coloana rosie si
    # bulbul sunt esentiale: un corp alb pe o tija alba se citeste ca o lingura,
    # rosul il face instrument de la prima privire.
    instr = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    di = ImageDraw.Draw(instr)
    tub_w = 0.042 * s
    sus_t, jos_t = 0.105 * s, 0.700 * s
    bulb_r = 0.072 * s
    bulb_c = jos_t + bulb_r * 0.55
    umbra, sticla, rosu = (24, 34, 46, 255), (247, 250, 252, 255), (211, 47, 47, 255)
    o = 0.012 * s  # contur intunecat, ca instrumentul sa se vada pe chihlimbar

    di.ellipse([c - bulb_r - o, bulb_c - bulb_r - o, c + bulb_r + o, bulb_c + bulb_r + o],
               fill=umbra)
    di.rounded_rectangle([c - tub_w - o, sus_t - o, c + tub_w + o, jos_t + o],
                         tub_w + o, fill=umbra)
    di.rounded_rectangle([c - tub_w, sus_t, c + tub_w, jos_t], tub_w, fill=sticla)
    di.ellipse([c - bulb_r, bulb_c - bulb_r, c + bulb_r, bulb_c + bulb_r], fill=rosu)
    col_w = tub_w * 0.42                                          # coloana rosie
    di.rounded_rectangle([c - col_w, 0.300 * s, c + col_w, jos_t], col_w, fill=rosu)
    for k in range(4):                                            # gradatii
        y = sus_t + (0.055 + 0.048 * k) * s
        di.rectangle([c - tub_w * 0.78, y, c - tub_w * 0.10, y + 0.010 * s],
                     fill=(120, 138, 156, 255))
    instr = instr.rotate(-8, resample=Image.BICUBIC, center=(c, 0.62 * s))
    strat.alpha_composite(instr)

    # conturul paharului: o singura linie franta, ca sa se lege curat in colturi
    pahar = [(c - sus_w, sus_y), (c - jos_w, jos_y), (c + jos_w, jos_y), (c + sus_w, sus_y)]
    d.line(pahar, fill=(232, 241, 248, 255), width=int(gros), joint="curve")
    for x, y in ((c - sus_w, sus_y), (c + sus_w, sus_y)):         # capete rotunjite
        d.ellipse([x - gros / 2, y - gros / 2, x + gros / 2, y + gros / 2],
                  fill=(232, 241, 248, 255))

    if zoom != 1.0:  # varianta mascabila: acelasi desen, mai mic, ca sa nu fie taiat
        mic = strat.resize((int(s * zoom), int(s * zoom)), Image.LANCZOS)
        strat = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        strat.alpha_composite(mic, (int((s - mic.width) / 2), int((s - mic.height) / 2)))

    img.alpha_composite(strat)
    return img.resize((S, S), Image.LANCZOS)


def main() -> None:
    for nume, S, zoom, rotunjit in (
        ("icons/icon-192.png", 192, 1.0, True),
        ("icons/icon-512.png", 512, 1.0, True),
        ("icons/icon-maskable-512.png", 512, 0.70, False),
        ("icons/apple-touch-icon.png", 180, 1.0, False),  # iOS pune el coltul rotund
        ("icons/favicon-32.png", 32, 1.0, True),
        ("icons/favicon-64.png", 64, 1.0, True),
    ):
        deseneaza(S, zoom, rotunjit).save(nume)
        print("scris", nume)


if __name__ == "__main__":
    main()
