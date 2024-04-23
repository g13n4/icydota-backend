import colorsys


def _hex_to_rgb(hex: str):
    if hex.startswith('#'):
        hex = hex[1:]

    rgb = []
    for i in (0, 2, 4):
        decimal = int(hex[i:i + 2], 16)
        rgb.append(decimal)

    return tuple(rgb)


def hex_to_rgb(hex: str) -> str:
    r, g, b = _hex_to_rgb(hex)
    return f'rgba({r}, {g}, {b}, 0.75)'


def hex_to_hsl(hex: str) -> str:
    rgb = colorsys.rgb_to_hls(*_hex_to_rgb(hex))
    colors = {letter: round(x, 2) for x, letter in zip(rgb, 'rgb')}
    return 'hsla({r}, {g}%, {b}%, 0.75)'.format(**colors)


dark = [
    "#e27c7c",
    "#a86464",
    "#6d4b4b",
    "#503f3f",
    "#333333",
    "#3c4e4b",
    "#456661",
    "#466964",
    "#599e94",
    "#6cd4c5",
]


light = [
    "#115f9a",
    "#1984c5",
    "#22a7f0",
    "#48b5c4",
    "#76c68f",
    "#a6d75b",
    "#c9e52f",
    "#f4f100",
    "#e1a692",
    "#de6e56",
    "#c23728",
]

print([hex_to_rgb(x) for x in dark])
print([hex_to_rgb(x) for x in light])
