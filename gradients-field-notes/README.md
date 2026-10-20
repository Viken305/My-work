# Field Notes — original grain-mesh gradients

8 original gradients (3000×2000 PNG) with a contact sheet and palette file.

| # | Name | Palette |
|---|---|---|
| 01 | Tidepool Ember | `#0B3C49 #1F6F78 #6FC2B0 #FF7A59 #FFD3B5` |
| 02 | Ultraviolet Dusk | `#140832 #4B1D7A #B0368F #F06E7C #FFC07A` |
| 03 | Matcha Static | `#0F2A1D #3E6B48 #9CC69B #E9F5DB #C9A93E` |
| 04 | Chrome Peach | `#2B2D42 #8DA9C4 #F6E7DA #F7A072 #E85D4A` |
| 05 | Midnight Citrus | `#050A30 #1B2CC1 #00C2A8 #C8F169 #F9F871` |
| 06 | Rosewater Smoke | `#2E1F27 #6E3B57 #B07A92 #E8C3CB #F7ECEE` |
| 07 | Solar Lichen | `#17181B #3B5A2A #8A9A3B #E0A800 #F2E8C9` |
| 08 | Glacier Bloom | `#3F5E8C #7FA7D6 #CFE6F2 #F7D6E0 #F28CB1` |

## How they're made

`make_gradients.py` places colour anchors on a domain-warped plane, blends them
in OKLab (so transitions stay vivid instead of muddy), adds a soft light sweep
and film grain. Every piece is seeded, so it re-renders identically.

```
pip install numpy pillow
python3 make_gradients.py out/                 # Field Notes
python3 make_gradients.py out2/ tide-and-dusk  # series 2
```

Edit `FIELD_NOTES` / `TIDE_AND_DUSK` (colours + seed) to make new ones.
