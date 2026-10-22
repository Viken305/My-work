# The Day the Earth Rang Like a Bell: narration and fact sheet

**Length: about 2:35–2:40** (346 words of narration ≈ 2:34, plus a ~4 s title card). That is under the 3:00 limit
for YouTube Shorts. For comparison, Krakatoa was 236 words and 1:45. If you want it under 2:00, cut part 6 down to E3
only and drop B3 (≈ 1:55).

Voice: Kokoro `af_heart` (US female, 1.05×), same as Krakatoa. The narration lines live in `script.py`, with numbers
written out in words so the voice says them correctly ("nineteen sixty"). The captions show the digits again
(`DISPLAY`).

| Part | Beat | Words | ≈ Time | Style frame |
|---|---|---|---|---|
| 1 | Hook: the planet rings, then "it started here", title | 38 | 0:00–0:21 | FIG 1, FIG 7 |
| 2 | The crack: plates, stuck for centuries, 3:11 pm, 1,000 km | 67 | 0:21–0:51 | FIG 2 |
| 3 | How big: 10 minutes, 9.5, ×32 per step, Haiti comparison | 49 | 0:51–1:13 | FIG 3, FIG 4 |
| 4 | The ocean: 25 m waves, across the Pacific, Hawaii, Japan | 70 | 1:13–1:44 | FIG 5 |
| 5 | The bell: the whole planet vibrates, 54-minute note | 64 | 1:44–2:13 | FIG 1 (callback) |
| 6 | What it left: volcano, sunken forests, ending | 58 | 2:13–2:38 | FIG 6 |

## Narration

**Part 1: hook**
1. In May 1960, the whole Earth started to ring. Like a bell.
2. Instruments around the world felt the planet itself swelling and shrinking, slowly. For days.
3. It was the biggest earthquake ever recorded. And it started here.
   *(title: THE DAY THE EARTH / RANG / like a bell)*

**Part 2: the crack**
4. Off the coast of Chile, one plate of the Earth's crust slides under another. Usually, it doesn't slide. It sticks.
5. For centuries, the strain kept building. Then, on the 22nd of May, at 3:11 in the afternoon, it let go.
6. A crack about 1,000 km long tore open along the coast. In places, the rock lurched by as much as 20 metres.

**Part 3: how big**
7. In the city of Valdivia, the ground shook for about 10 minutes.
8. Scientists rated it 9.5. Every step up that scale means about 32 times more energy.
9. So this one released thousands of times more energy than the earthquake that destroyed Haiti's capital in 2010.

**Part 4: the ocean**
10. Then the sea moved. Waves up to 25 metres high hit the coast of Chile. Somewhere between 1,000 and 6,000 people died.
11. But the tsunami kept going, across the entire Pacific, almost as fast as a passenger jet.
12. 15 hours later, it struck Hawaii and killed 61 people. Almost a day later, it reached Japan, 17,000 km away, and
    killed about 140 more.

**Part 5: the bell**
13. And the energy didn't stay near Chile. It travelled through the whole planet, until the Earth itself started to vibrate.
14. Its deepest note was one slow swing, about every 54 minutes. A bell far too low to hear.
15. It was the first time scientists clearly heard the whole planet ring. And its notes told them what the inside of
    the Earth is like.

**Part 6: what it left behind**
16. Two days after the quake, a volcano nearby erupted.
17. Parts of the coast sank by about 2 metres. The sea flooded in, and whole forests drowned. Many of those dead trees
    are still standing in the water today.
18. Since then, instruments have heard the Earth ring after every great earthquake. But never as loudly as in 1960.

## Fact sheet

| Claim | Check |
|---|---|
| 22 May 1960, 15:11 local time (19:11 UTC) | USGS. A magnitude 8.1–8.2 foreshock hit Concepción the day before (not used) |
| Magnitude 9.5, the largest ever recorded | USGS gives 9.5; published estimates range from 9.4 to 9.6 |
| Shaking lasted about 10 minutes | Widely cited (USGS, Britannica). We say "about" |
| Rupture about 1,000 km long | Estimates are 800–1,000 km. We say "about". The red line on the inset map is illustrative |
| Slip "as much as 20 metres" | Models give an average of about 17–20 m and peaks above 20 m (some up to ~40 m), so "as much as 20" is safe |
| Nazca plate moves ~7 cm a year (FIG 2 label) | Convergence is about 6.5–8 cm a year |
| Tsunami up to 25 m on the Chilean coast | Commonly cited maximum run-up (NOAA/USGS) |
| 1,000–6,000 deaths in Chile | USGS lists 1,655. Other estimates run up to about 6,000. We give the range |
| Hawaii: about 15 hours later, 61 killed in Hilo | NOAA/USGS |
| Japan: about 22 hours later, about 140 killed | Usually given as 138–142. We say "almost a day" and "about 140" |
| 17,000 km to Japan | Great-circle distance from the epicentre to the Sanriku coast is 16,995 km (computed in `ink.gc_km`) |
| "Almost as fast as a passenger jet" (FIG 5: ~750 km/h) | 10,654 km to Hilo in 15 h is ~710 km/h, and 17,000 km in ~22 h is ~770 km/h. Jets cruise at ~850–900 km/h |
| Energy ×32 per whole step of magnitude | Standard (10^1.5 ≈ 31.6) |
| "Thousands of times" Haiti (FIG 4: ≈5,800×) | 32^(9.5−7.0) ≈ 5,800. With the 9.4–9.6 range it is ~4,000–8,000×, so the narration says "thousands" |
| FIG 4 square areas | Each area is the energy ratio: 9.1 is a quarter of 9.5, 8.0 is 0.55%, 7.0 is 0.017% |
| The Earth rang (free oscillations) for days | 1960 gave the first clear, confirmed records of Earth's free oscillations (Benioff, Press & Smith 1961; Ness, Harrison & Slichter 1961; Alsop, Sutton & Ewing 1961) |
| Deepest note about every 54 minutes | The gravest mode, 0S2 ("football mode"), has a period of 53.9 min. The "breathing" mode 0S0 (20.5 min) is the swelling and shrinking in line 2 |
| Strain meter in California (FIG 1 card) | The Benioff strainmeter at Isabella, California, recorded the modes. The trace on the card is drawn from a model, not scanned |
| The notes revealed the Earth's interior | Mode frequencies constrain density and elasticity with depth (simplified in the narration) |
| Volcano erupted two days later | Cordón Caulle (Puyehue–Cordón Caulle) began erupting on 24 May, ~38 h after the main shock |
| Coast sank by about 2 m; drowned "ghost forests" | Subsidence around Valdivia was ~1.5–2.7 m. Dead, still-standing trees in tidal marshes are documented (Atwater et al.). **Find a current photo before posting** to confirm "still standing today" |
| "Never as loudly as in 1960" | 1960 is still the largest event by seismic moment, so its modes were the strongest recorded |
| Not used | Effects on Earth's rotation or day length (weak sources for 1960); the Riñihue lake flood ("Riñihuazo"), which is a good story but would add ~15 s |
