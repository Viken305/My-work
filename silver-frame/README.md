# Silver ornamental frame — 3D printable

Parametric, print-ready frame body matching the silver frame reference: 2:1 outer
ratio, 1 in (25.4 mm) border on every side.

**Status:** frame body done. The carved ornaments (corner rosettes, top/bottom
centre scroll panels, side flowers, acanthus scrollwork) are **not** modelled
yet. They go on the flat "ornament field" band once close-up references are ready.

## Files

| File | What |
|---|---|
| `frame.py` | Generator: profile sweep with mitered corners, back rebate, keyholes, split into halves |
| `preview.py` | Renders `out/preview.png` (views + cross-section) |
| `out/frame_full.stl` | One piece, 381 × 190.5 × 15.4 mm, needs a bed of 390 mm or more |
| `out/frame_left.stl`, `out/frame_right.stl` | Two halves, 190.5 × 190.5 mm each, fit a 220 mm or larger bed |
| `out/report.json` | Parameters + mesh stats |

```
pip install manifold3d numpy matplotlib
python frame.py                 # default: 15 x 7.5 in outer
python frame.py --width-in 20   # 20 x 10 in outer, still 1 in border
python preview.py
```

## Default dimensions (mm)

- Outer: 381 × 190.5 (15 × 7.5 in). Sight opening: 330.2 × 139.7 (13 × 5.5 in)
- Border: 25.4 (1 in) all round. Thickness: 15.4 at the outer bead, 12.0 on the ornament field
- Profile, outer edge to inner edge: half-round outer bead (r 2.4), cove, flat ornament
  field (5.8 to 17.4 mm in), inner bead, step, small bead, slope down to the sight edge
- Back rebate: 6.35 wide × 6.0 deep. Fits glass/acrylic + print + backer cut to
  342.9 × 152.4 mm (13.5 × 6 in) minus about 0.5 mm clearance
- 2 undercut keyholes in the back of the top rail (8 mm head, 4 mm neck) for screws
- Halves: 4 alignment-pin holes (2.0 mm dia, 8 mm deep each side) at the seam.
  Use pieces of 1.75 mm filament as pins, plus CA glue or epoxy

## Printing

- Orientation: face up, flat back on the bed
- Supports: **on build plate only**. Needed for the rebate ledge, a 6.35 mm overhang
  around the opening. Keyholes and pin holes print without supports
- 0.12 to 0.16 mm layers for the beads and, later, the carving. 3 walls, 15 % gyroid
- Silver look: silk silver PLA, or grey primer + metallic silver paint + a dark wash
  rubbed back so the carving reads
