# The Day the Sun Hit Us: style guide

A 9:16 Short (**about 2:20**) about the Carrington Event of 1–2 September 1859, rendered entirely in code for
@BrighterMinds. Style frames: `python3 frames.py` writes `out/style/frame_*.png` and the contact sheet
`out/style/style_frames.png`.

This style is new. It is not the cyanotype of `krakatoa/`, the graphite noir of `deep-hole/` or the bone-paper
seismogram of `valdivia/`. This one is **"Magic Lantern"**: every scene is a hand-painted glass slide thrown onto a
screen in a dark room, which is how audiences in 1859 actually saw science. The story is about light (a flare, an
aurora, sparks in the wires), so the film is built from projected light on black glass.

## 1. Big idea
- **A lantern show.** Each scene is a numbered slide (`SLIDE 3 · THE CROSSING`) with a cream paper label and a red
  thumb-spot, like real lantern slides. Transitions are lantern moves: iris closes, two-lantern dissolves, slip-slide
  wipes.
- **Light is the hero.** The Sun, the cloud, the aurora and the current in the wires are the only things that glow.
  They are additive light with halation. Everything else is engraved linework on dark glass.
- **The needle drives the film.** One signal (`lantern.magnetogram`, the Kew needle) is the master clock. It is quiet,
  gives one small twitch at the flare, then the storm drives it off the scale. Its value drives projector flicker, wire
  sparks, caption jitter and the sound mix.

## 2. Palette
| Role | Colour | Hex |
|---|---|---|
| The dark room, opaque glass | Lantern black | `#0D0B0F` |
| Night glass | Plum black | `#1B1624` |
| Sky dye | Indigo | `#2C2252` |
| All linework and text | Limelight | `#FFF2D8` |
| Secondary labels | Silver | `#968E88` |
| Paper (labels, the screen, the tape, the magnetogram) | Card | `#ECDEBE` with sepia ink `#5C4630` |
| **The Sun and everything it throws** | Solar gold | `#FFB234`, white-hot `#FFFCF0` for the flare only |
| **The sky's answer: the aurora** | Oxygen green `#54FFA8`, oxygen crimson `#FF4068` |
| **Electricity in our wires** | Spark blue | `#96D6FF` |

Rules:
- Gold means **the Sun**, green and crimson mean **the aurora**, blue means **current in human wires**. They never swap.
- White-hot appears in one place only: Carrington's two flare beads (and the title).
- Cream paper is the only "lit" surface that is not light. It marks a real historical document (Carrington's drawing,
  the Kew magnetogram, the Boston telegraph tape).

## 3. Texture and rendering (`lantern.py`)
- **Glass:** warm black with a faint mottle and horizontal brush drag in the varnish.
- **Engraving:** limelight lines with a little halation, like light leaking through a scratch. Hatching for shade.
- **Hand tint:** transparent dye laid in by brush (mottled alpha), soft-edged and 3–6 px off-register from the
  engraving.
- **Light:** four-pass additive glow (wide bloom, tight bloom, colour line, white core).
- **Sun:** limb-darkened disc with granulation, faculae near the edge, engraved sunspots, layered corona.
- **Aurora:** folded curtains of vertical rays with a green-to-crimson gradient and a sharp bright green hem.
- **Post (the projector):** a soft slide mat at the frame edge, lamp hot-spot falloff, halation on true highlights
  only, lens fringing, a 1–2% limelight flicker, gentle gate weave, dust and hairs on the glass, and grain.

## 4. Typography
- **Captions:** *Inter Display* Bold in limelight.
- **Emphasis:** *Noto Serif Display* Bold Italic in the colour of what it means (`blinding` white-hot, `us` gold,
  `read` aurora green, `sky` aurora green, `nine days` crimson), with a halo in that colour.
- **Labels:** *Noto Sans Mono*, tracked caps. Slide labels are sepia on cream.
- **Title:** `THE DAY THE SUN` in serif roman caps, then a huge gold italic **Hit Us** glowing like the Sun.

## 5. Captions that interact with the graphics
- **Projected into focus:** every letter arrives large, soft and split into red/blue fringes, then snaps sharp, like a
  lantern being focused.
- **Flare ignition:** `blinding` lights up white at the exact frame the beads flare. It halates, then cools to gold.
- **Riding the cloud:** `17.6 HOURS` is written along the leading edge of the cloud and travels with it to Earth.
- **On a field line:** `squeezed` rides the outer magnetic field line and is compressed with it when the cloud hits.
- **Lit by the aurora:** `read` picks up its colour from the curtain light sweeping over it.
- **Morse tape:** the Boston–Portland message prints out of the register as dots, dashes and pencilled letters, then
  the tape scorches and burns from the end.
- **Needle jitter:** during the storm the active word shakes with the magnetogram value.
- Captions stay above y = 1480 so the Shorts interface never covers them.

## 6. Motion
- Slow, deliberate lantern moves between slides (iris, dissolve, slip). Inside a slide, modern motion: springs, ease-out
  expo, parallax between glass layers (stars, curtains, mountains, foreground).
- One violent beat: the cloud's arrival. Flicker spikes, the needle leaves the paper, everything jolts once.
- 3-sample motion blur. Counters are frame-locked so digits never smear.

## 7. Sound (planned)
- Projector hum and the clack of slides changing. Pen-on-card for Carrington's sketch. A rising solar roar for the
  cloud, a deep thud on impact, crackling aurora shimmer (a high glassy pad), Morse sounder clicks for the telegraph
  (spelling the real message), sparks. A music-box style theme in a minor key for the Victorian feel.
