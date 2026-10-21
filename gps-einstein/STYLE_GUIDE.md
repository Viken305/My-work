# Your Phone Does Einstein's Math: style guide

A 9:16 Short (**~1:50**) about why GPS only works because of Einstein's relativity, rendered in code for
@BrighterMinds.

The style is new. It is not Kurzgesagt flat shapes, not the graphite noir of `deep-hole/`, not the cyanotype of
`krakatoa/` and not the static of `ai-images/`. This one is **"Frosted Glass"**: a dark, quiet studio where every
object (the phone, Earth, the satellites, the clocks, even the numbers) is a panel of frosted glass that light passes
through. It should feel like a premium product film. The hero of the video is **time made visible**: clocks, ticks and
pulses of light.

## 1. Big idea
- **Everything is glass, and light tells the story.** Signals are beams and rings of light; distance is how far
  light travelled; a wrong clock shows up as a dot that slides off the map. Glass makes the light visible as it bends.
- **Two clocks, always.** Whenever time matters, a GROUND clock and an ORBIT clock sit side by side so the drift
  between them can be seen.
- **Calm, precise motion.** Slow camera orbits, eased moves and no shaking. The only fast thing is the satellite
  streaking past at 14,000 km/h.

## 2. Palette
Set in `project.json` → `style.palette` (editable in the dashboard).

| Key | Hex | Role |
|---|---|---|
| `ink` | `#050A18` | background, deep navy black |
| `carbon` | `#0B1630` | background gradient, floor, far glass |
| `card` | `#1A2A4A` | glass tint (drawn at 25–45 % opacity over a blurred copy of the scene) |
| `paper` | `#F4F7FB` | main text, glass edge highlights |
| `smoke` | `#8C9BB5` | labels, units, secondary text |
| `amber` | `#FFC27A` | **you and the signal**: your phone, the blue dot's trail, distances (caption list `words`) |
| `violet` | `#A99BFF` | **time and Einstein**: clocks, µs counters, relativity (caption list `model`) |
| `cyan` | `#7FE3FF` | light beams, signal rings, the map's blue dot |

Rainbow caustics are the only place the full spectrum appears, as thin, faint bands where light leaves the glass.

## 3. Glass and rendering
- **Frosted glass panel** = blur the scene behind it (gaussian, radius ~24 px at 1080 px wide), tint with `card`,
  add a 1–2 px `paper` rim light on the edge that faces the key light, a soft inner shadow on the opposite edge, and
  very fine noise so the surface doesn't look flat.
- **Refraction:** the scene behind a glass object is slightly displaced (a smooth normal map, max ~12 px) and split
  by colour (`style.post.ca`) only near the edges, like dispersion in a prism.
- **Caustics:** a moving pattern of light bands on the floor and on the panels behind (`style.post.caustics`),
  drifting slowly. These are what make it look premium, so never leave them static.
- **Depth of field:** three planes. Far glass shapes in the background are blurred and dim; the hero sits sharp in
  the middle; one or two out-of-focus glass shards drift past in front (`style.post.dof`).
- **Light:** one key light, top left. Bloom only on `cyan` beams, `amber` dots and clock hands (`style.post.bloom`).
- Post: light grain (0.5), motion blur with 3 sub-frames, gentle vignette, no glitch.
- All art is vector or procedural, drawn in code (`vector_only`).

## 4. Typography
- **Inter Display Light** for titles in large sizes, with tight tracking. Title letters are glass themselves
  (blurred interior, rim light, caustic sweep).
- **Inter Display Medium** for labels; **Noto Sans Mono** for every clock, counter, frequency and µs readout. Digits
  tick and roll like a real instrument instead of fading.
- Units are always shown in `smoke`, smaller than the number: **38** µs / day.

## 5. Captions
- 3 words at most, size 80, centred at y = 1380 (`style.captions`). White text on a small frosted-glass pill that
  lightly blurs whatever is behind it.
- Highlighted words: `words` list → `amber`, `model` list → `violet`, with a soft glow. Numbers are spoken as words
  and shown as digits through `display` ("thirty eight microseconds" → "38 µs").

## 6. Sound design
- Bed: an airy, slow synth pad with a quiet, steady clock tick underneath (the tick is the motif of the film).
- Glass sounds: chimes, clinks and soft ringing tails for things appearing; pulses for signals; a warm lock chime
  every time two clocks sync.
- When time is wrong, the tick detunes or phases; when the fix lands, everything resolves to one clean tick.
- Mix: voice first, music −14 LUFS overall (`audio`).

## 7. Story (hook first) and duration
| Part | Lines | Beat |
|---|---|---|
| 1 Hook | H1–H3 | Glass phone, blue dot drifts 10 km a day, coffee-shop miss, title. |
| 2 Clocks in the sky | A1–A3 | Orbit, 30 satellites, atomic clocks broadcast where + when, the delay = distance. |
| 3 Four satellites | B1–B3 | Three spheres → a point, the 4th fixes the phone clock, 1 µs = 300 m. |
| 4 Einstein's problem | C1–C4 | Ground vs orbit clocks: speed −7 µs, weak gravity +45 µs, net +38 µs / day. |
| 5 Fix and payoff | D1–D3 | Clocks tuned slow before launch, the what-if world, loop back to the phone. |

16 shots are listed in `project.json` → `shots`. The last frame matches the first so the Short loops.

## 8. Fact sheet
| Claim | Value used | Note |
|---|---|---|
| Orbit height | ~20,200 km → "twenty thousand kilometres" | medium Earth orbit |
| Satellites | ~31 operational → "about thirty" | the count changes as satellites are replaced |
| Orbital speed | ~3.9 km/s ≈ 14,000 km/h | |
| Special relativity (speed) | clocks lose ~7 µs / day | |
| General relativity (weaker gravity) | clocks gain ~45 µs / day | |
| Net | +38 µs / day | |
| Light per µs / ns | ~300 m / ~30 cm | |
| Drift if uncorrected | 38 µs × c ≈ 11 km / day → "about ten kilometres" | widely quoted figure |
| Clock fix | 10.22999999543 MHz on the ground instead of 10.23 MHz | factory offset |
| Signal travel time | ~0.067 s from 20,200 km | shown on screen in A3 |
| Satellites needed | 4: three for position, one for the receiver's clock | simplified: three spheres meet at two points, one is far out in space |
