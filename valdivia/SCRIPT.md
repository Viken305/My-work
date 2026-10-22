# The Day the Earth Rang Like a Bell: narration and fact sheet

**Final length: 2:25** (145 s across 6 parts; under the 3:00 Shorts limit).

Voice: Kokoro `af_heart` (US female, 1.05×), same as Krakatoa. The narration lines live in `script.py`, with numbers
written out in words so the voice says them correctly ("nineteen sixty"). The captions show the digits again
(`DISPLAY`).

**Fact-check changes before the final render**
- "Waves up to 25 metres" → **"more than 10 metres"**. 25 m appears mainly on Wikipedia; other sources give ~8–15 m locally.
- "About a thousand km" → **"nearly a thousand km"**. Plafker & Savage (1970) give ~1,000 km; a 2012 inversion gives ~800 km.
- "Many of those dead trees are still standing today" → **cut**. The drowned forests are documented (Cisternas, Atwater
  et al.), but trees still standing today could not be confirmed. Replaced with "fields turned into tidal flats" (same source).
- "Sank by about 2 m" → **"by up to 2 m"** (1–2 m regionally, ~1.5 m at Maullín).

## Narration

**Part 1: hook**
1. In May 1960, the whole Earth started to ring. Like a bell.
2. Instruments around the world felt the planet itself swelling and shrinking, slowly. For days.
3. It was the biggest earthquake ever recorded. And it started here.
   *(title: THE DAY THE EARTH / RANG / like a bell)*

**Part 2: the crack**
4. Off the coast of Chile, one plate of the Earth's crust slides under another. Usually, it doesn't slide. It sticks.
5. For centuries, the strain kept building. Then, on the 22nd of May, at 3:11 in the afternoon, it let go.
6. A crack nearly 1,000 km long tore open along the coast. In places, the rock lurched by as much as 20 metres.

**Part 3: how big**
7. In the city of Valdivia, the ground shook for about 10 minutes.
8. Scientists rated it 9.5. Every step up that scale means about 32 times more energy.
9. So this one released thousands of times more energy than the earthquake that destroyed Haiti's capital in 2010.

**Part 4: the ocean**
10. Then the sea moved. Waves more than 10 metres high hit the coast of Chile. Somewhere between 1,000 and 6,000 people died.
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
17. Parts of the coast sank by up to 2 metres. The sea flooded in. Whole forests drowned, and fields turned into tidal
    flats.
18. Since then, instruments have heard the Earth ring after every great earthquake. But never as loudly as in 1960.

## Fact sheet

| Claim | Check |
|---|---|
| 22 May 1960, 15:11 local time (19:11 UTC) | USGS. A magnitude 8.1–8.2 foreshock hit Concepción the day before (not used) |
| Magnitude 9.5, the largest ever recorded | USGS gives 9.5; published estimates range from 9.4 to 9.6 |
| Shaking lasted about 10 minutes | Widely cited (USGS, Britannica). We say "about" |
| Rupture nearly 1,000 km long | Plafker & Savage 1970 (USGS): ~1,000 km; later inversion ~800 km. We say "nearly". The red line on the map is illustrative |
| Slip "as much as 20 metres" | Models give an average of about 17–20 m and peaks above 20 m (some up to ~40 m), so "as much as 20" is safe |
| Nazca plate moves ~7 cm a year (FIG 2 label) | Convergence is about 6.5–8 cm a year |
| Waves more than 10 m on the Chilean coast | Local heights of ~8–15 m are reported; some sources cite up to 25 m, which we do not use |
| 1,000–6,000 deaths in Chile | Estimates vary widely (USGS-cited 1,655; Wikipedia 1,886–6,000). We give the range and say so on screen |
| Hawaii: about 15 hours later, 61 killed in Hilo | ~14.8 h first arrival; 61 dead (RMS/NOAA; one USGS circular gives 56) |
| Japan: about 22 hours later, about 140 killed | Britannica: Honshu 22 h after, 138 killed (other sources 142). We say "almost a day" and "about 140" |
| 17,000 km to Japan | Great-circle distance from the epicentre to the Sanriku coast is 16,995 km (computed in `ink.gc_km`) |
| "Almost as fast as a passenger jet" (FIG 5: ~750 km/h) | 10,654 km to Hilo in 15 h is ~710 km/h, and 17,000 km in ~22 h is ~770 km/h. Jets cruise at ~850–900 km/h |
| Energy ×32 per whole step of magnitude | Standard (10^1.5 ≈ 31.6) |
| "Thousands of times" Haiti (FIG 4: ≈5,800×) | 32^(9.5−7.0) ≈ 5,800. With the 9.4–9.6 range it is ~4,000–8,000×, so the narration says "thousands" |
| FIG 4 square areas | Each area is the energy ratio: 9.1 is a quarter of 9.5, 8.0 is 0.55%, 7.0 is 0.017% |
| The Earth rang (free oscillations) for days | Benioff saw a hint in 1952 (Kamchatka); 1960 gave the first clear, confirmed records of Earth's free oscillations (Benioff, Press & Smith 1961; Ness, Harrison & Slichter 1961; Alsop, Sutton & Ewing 1961) |
| Deepest note about every 54 minutes | The gravest mode, 0S2 ("football mode"), has a period of 53.9 min. The "breathing" mode 0S0 (20.5 min) is the swelling and shrinking in line 2 |
| Strain meter in California (FIG 1 card) | The Benioff strainmeter at Isabella, California, recorded the modes. The trace on the card is drawn from a model, not scanned |
| The notes revealed the Earth's interior | Mode frequencies constrain density and elasticity with depth (simplified in the narration) |
| Volcano erupted two days later | Cordón Caulle began erupting on 24 May, 38 h after the main shock (SERNAGEOMIN) |
| Coast sank by up to 2 m; forests drowned; fields became tidal flats | Valdivia estuary 1–2 m (Nelson et al.); Río Maullín ~1.5 m, "killed forests and changed pastures into tidal flats" (Cisternas, Atwater et al., GSA 2003) |
| "Never as loudly as in 1960" | 1960 is still the largest event by seismic moment, so its modes were the strongest recorded |
| Not used | Effects on Earth's rotation or day length (weak sources for 1960); the Riñihue lake flood ("Riñihuazo"), which is a good story but would add ~15 s |
| FIG 8: later quakes ring more quietly | Bars scaled by seismic moment (10^(1.5·ΔM)): 1964 Alaska 9.2, 2004 Sumatra 9.1, 2011 Japan 9.1, 2010 Chile 8.8 |
| "0.0003 Hz" | 1 / (53.8 min × 60 s) ≈ 0.00031 Hz |
