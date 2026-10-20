# How AI Draws From Nothing: style guide

A 9:16 Short (**~1:50**) about how an AI image model turns a sentence into a picture, rendered in code for
@BrighterMinds.

The style is new. It is not Kurzgesagt flat shapes, not the graphite noir of `deep-hole/`, and not the cyanotype of
`krakatoa/`. This one is **"Static & Signal"**: a dark studio where every picture starts as TV static and is pulled
into focus, one step at a time. The hero of the video is **the noise itself**: we watch it turn into a picture.

## 1. Big idea
- **Everything starts as static.** Every image, every caption word, even the title, arrives by denoising out of
  grain. The viewer learns the core idea from the visual language before the narrator says it.
- **Every picture is vector art drawn in code** (`art.py`): the astronaut cat, its seed variants, Paris, and the
  training examples. No AI-generated images are used. The noising uses the real diffusion maths on those drawings;
  the step-by-step guesses, attention glows and number barcodes are simplified illustrations of what a model does,
  and are labelled as such on screen where it matters.
- **Words are amber, the model is violet.** The prompt is something you say; the model is something that listens.
  Two colours, two characters, used the same way all video.

## 2. Palette
| Role | Colour | Hex |
|---|---|---|
| Background (studio black, slightly warm) | Carbon | `#0E0D12` → `#07070A` |
| Text, UI lines, pixels | Paper white | `#F2EFE9` |
| Secondary text, grids, ticks | Smoke | `#8A8794` |
| **Accent 1: your words, the prompt** | Amber | `#FFB547` |
| **Accent 2: the model, attention, maths** | Electric violet | `#8B6CFF` |
| Static / noise | Full-colour RGB grain, shown desaturated except in the hook | — |

Rules:
- Black and white do 85% of the work. Amber means **words**, violet means **the model thinking**. They never swap.
- When a word "lights up" part of an image, the glow is amber on top of the picture (word → place).
- The finished images are the **only** full-colour things on screen, so each one lands like a reveal.

## 3. Texture and rendering
- **Studio grain:** fine, moving film grain over everything; slightly stronger in the corners.
- **Image tiles:** each picture sits on a floating card with soft shadow, thin white frame, rounded 18 px corners,
  and a mono label strip underneath (`STEP 12 / 30 · SEED 1883`).
- **Noise is real noise:** Gaussian per-pixel noise, mixed with the image using a standard diffusion noise schedule, so the
  "forward" noising in part 3 is mathematically the same process the model was trained on.
- **Token chips:** prompt words split into rounded chips; each chip unfolds into a column of 768 thin bars
  (an illustrative embedding, drawn as a barcode).
- **Meaning map:** a dark 3D point cloud of words (cat near kitten, moon near planet), slowly orbiting, depth of
  field, points glow when mentioned.
- **Attention threads:** amber curves from a token chip down into the picture, ending in a soft heat map taken from
  the drawing's own layers for that word.
- **Camera:** smooth push-ins and match cuts: static → TV screen → image tile; a token chip → a point in the
  meaning map; a small latent grid → the full-size picture.
- **Post:** motion blur (3 samples), bloom only on amber and violet, gentle chromatic aberration at the edges, grain,
  vignette. Hard cuts only at the title.

## 4. Typography
- **Captions:** *Inter Display* Bold, paper white.
- **Emphasis words:** *Noto Serif Display* Italic. Prompt words (prompt, words, cat, moon) in **amber**; model words
  (noise, step, guess, model) in **violet**.
- **Prompts on screen:** *Noto Sans Mono*, typed live with a blinking caret, in an amber-edged input box.
- **Technical labels:** *Noto Sans Mono*, small, tracked caps: `FIG. 2 · TEXT ENCODER`, `64 × 64 × 4 LATENT`.
- **Title:** `HOW AI DRAWS / FROM NOTHING`, resolving out of static.

## 5. Captions (premium, new for this video)
The caption system matches the topic: **every word denoises into place.**

1. **Word-by-word reveal timed to the real voice** (the pause-matching aligner from `deep-hole/` and `krakatoa/`).
2. **Denoise-in:** each word starts as a small rectangle of coloured static the size of the word, then resolves to
   sharp letters in ~6 frames (we literally blend noise → glyph with the same schedule as the model).
3. **Loudness drives weight:** the active word swells slightly with the voice envelope (reuse `VoiceEnvelope`).
4. **Emphasis words** switch to serif italic in amber or violet, with a single scan-line sweep across them.
5. **Numbers** are counters on the visuals: step `1 → 30`, `768` numbers per word, `48×` smaller, seed values.
6. **Exit:** words dissolve back into grain, left to right.
7. **Layout:** max 3 words per phrase, centred at y≈1380, never below y=1480, nothing in the top ~220 px or on the
   right side between y 900–1520 (Shorts UI).

## 6. Sound design
- **Static:** real filtered white noise whose loudness follows how noisy the image is. As the picture forms, the hiss
  falls away into a clean tone. The viewer *hears* denoising.
- **Each step:** a soft tick, gently rising in pitch from step 1 to 30, plus a glassy shimmer on the final step.
- **Typing:** quiet mechanical key clicks for prompts.
- **Tokens:** a small "snap" as the sentence splits into chips; a data "sparkle" as each becomes numbers.
- **Attention threads:** a thin string-like pluck when a word connects to the image.
- **Music:** a minimal synth pulse (warm analogue pad + soft arpeggio) that becomes more harmonic as images
  resolve; silence for one beat before the final reveal.
- **Master:** ducking under the voice, -14 LUFS, true peak -1.2 dB, linear gain + limiter (same as `krakatoa/`).

## 7. Story (hook first) and duration
**Total: about 1:50** (5 parts, ~260 spoken words at our usual pace). Shorts allow up to 3:00, so there is room,
but under 2:00 keeps retention high.

| Part | Time | What happens |
|---|---|---|
| 1. Hook | 0:00–0:16 | Full-screen static. A prompt types itself: *"a cat wearing an astronaut suit riding a bicycle on the moon, digital art"* In 2 s the static pulls into the picture. "This picture started as pure noise. No photo. No sketch. Just static." Title resolves from grain. |
| 2. Reading your words | 0:16–0:38 | The prompt splits into tokens. Each becomes 768 numbers. The chips fly into a meaning map where *cat* sits near *kitten* and *moon* near *planet*. "It doesn't read words. It reads where they sit in a map of meaning." |
| 3. How it learned | 0:38–0:58 | Billions of captioned images rush past. One photo gets noisier step by step until it is static. "Its whole training is one tiny job: look at a noisy picture and guess the noise." |
| 4. Making the picture | 0:58–1:30 | A new seed of random static. Step counter 1 → 30, simulated steps: blurry blobs of colour first, then shapes, then fur and craters. Amber threads show *cat* lighting up the cat and *moon* lighting up the ground. Guidance: the same step with and without the prompt, side by side; the model pushes further toward your words. A small 64×64 latent grid blows up into the full picture ("it works on a picture 48 times smaller, then a decoder paints the pixels"). |
| 5. Same words, new noise | 1:30–1:50 | Four seeds, same prompt: four different cats. Same seed again: the identical cat. "Every AI image is random noise, sculpted by your words." The final image dissolves back to static, which loops to the hook. |

**Image examples** (all vector illustrations in `art.py`):
- Hero: *a cat wearing an astronaut suit riding a bicycle on the moon* with 30 simulated steps.
- Seed grid: the same prompt, 4 "seeds" (different cat, bike colour, sky, pose).
- Prompt edit: *"…on the moon"* vs *"…in Paris"* with the same seed (same pose, new world).
- Guidance: the same seed at guidance 1 vs 7.5 (mush vs clear subject).
- Training strip: 3 simple pictures (a dog, a mountain, a lighthouse) being noised.

## 8. Production notes
- **No AI-generated images** (decision, Oct 2026). All pictures are vector illustrations in `art.py`.
- **Simulated steps:** the model's guess at step k = the drawing blurred by a shrinking amount plus fading noise
  (coarse first, detail last, which is how real models behave). The forward noise uses the real cosine schedule.
- **Attention glows** come from the drawing's own layers (the cat layer for "cat", the ground for "moon").
- **Number barcodes and the meaning map** are illustrative and labelled "illustration" / "simplified".
- **Storyboard:** `python3 storyboard.py` -> `out/storyboard_1..3.png`.

## 9. Fact sheet (status)
| Claim | Status |
|---|---|
| Diffusion models start from random noise and remove it over many steps, guided by the text | Confirmed (DDPM 2020, Latent Diffusion 2022) |
| Training: add noise to real images, the model learns to predict that noise | Confirmed; this is the standard training objective |
| Trained on billions of image–caption pairs | Confirmed for SD (LAION-5B subset). Said as "billions" |
| Prompt split into tokens; each becomes a list of numbers (768 in SD 1.5's CLIP text encoder), max 77 tokens | Confirmed |
| Similar meanings sit close together in that number space | Confirmed (embedding geometry); our 3D map is a projection, labelled as such |
| Works in a compressed 64×64×4 latent for a 512×512 image (48× fewer numbers), a decoder makes the pixels | Confirmed (512·512·3 / 64·64·4 = 48) |
| Cross-attention links words to image regions | Confirmed; we show simplified glows |
| Guidance compares a prediction with and without the prompt and pushes toward the prompt (scale ~7.5) | Confirmed (classifier-free guidance) |
| Coarse layout appears first, fine detail last | Confirmed; our simulated steps follow it |
| Same prompt + same seed + same settings = same image | Confirmed (deterministic on the same setup) |
| "All AI image models work this way" | **Not said.** Newer models (SD3, FLUX) use transformers and flow matching, and some generate differently; we say "most image generators" and "the basic idea" |
| "It copies and pastes pieces of training images" | **Not said**; it is a misconception. We avoid making claims about copying either way |
