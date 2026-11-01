# Why Borders Are Shaped the Way They Are: script, facts, sources

A full-screen **3D globe flythrough**, about 2:22.
- One camera flies over a real globe (Natural Earth data) from story to story.
- Borders burn on as glowing lines, countries rise as 3D slabs, and mountains stand up along ridges.
- Chapter cards play during the flights.

Shot list with running times: `SHOTS.md`. The earlier flat "Paper Atlas" version is kept in `film_atlas.py`, `render_atlas.py` and `shots_atlas.py`.

Narration: `script.py`, in chapters: The Hook · Nature · Straight Lines · Deals · Accidents · The Story.

## Fact check

| Claim | Basis | Source |
|---|---|---|
| The Rio Grande moved south, and El Chamizal ended up on the US side | Floods in the 1860s (notably 1864) shifted the river south, leaving about 600 acres (2.4 km²) north of it | U.S. National Park Service, Chamizal National Memorial |
| About a hundred years of arguing, until 1963 | The dispute ran from the 1860s to the Chamizal Convention of 1963, which handed the land back (transfer completed in 1967), with the river put into a new concrete channel | Chamizal Convention (1963) |
| Chile is long and thin between the Andes and the Pacific | About 4,300 km long and on average about 180 km wide. Its border with Argentina follows the Andes (1881 Boundary Treaty: highest peaks and the water divide). | *Encyclopaedia Britannica*, "Chile"; Boundary Treaty of 1881 |
| Point Roberts: US land you reach through Canada | The tip of the Tsawwassen peninsula lies south of the 49th parallel, so it is part of Washington State, but its only land route runs through British Columbia | *Encyclopaedia Britannica*, "Point Roberts"; Oregon Treaty (1846) |
| Berlin Conference badge (1884) | The conference ran November 1884 – February 1885 | Herbst (2000) |
| Bir Tawil: two lines, claimed by no one | The 1899 Anglo-Egyptian agreement put the border on the 22nd parallel; a 1902 administrative line moved it in two places. Egypt claims the 1899 line (Bir Tawil would be Sudan's) and Sudan the 1902 line (Bir Tawil would be Egypt's), so neither claims its about 2,060 km² | Anglo-Egyptian Condominium Agreement (1899); *Encyclopaedia Britannica*, "Bir Tawil" |
| The Rio Grande is part of the US–Mexico border | The river forms about 2,019 km (1,254 mi) of the border, from El Paso to the Gulf of Mexico | International Boundary and Water Commission (IBWC) |
| The Pyrenees divide France and Spain | The Treaty of the Pyrenees (1659) took the mountains as the boundary; the line was fixed along the range by the Treaties of Bayonne (1856–1868) | Sahlins, *Boundaries: The Making of France and Spain in the Pyrenees* (1989) |
| 1818, US and Britain, 49th parallel | The Anglo-American Convention of 1818 set the border on the 49th parallel from Lake of the Woods to the Rocky Mountains; the Oregon Treaty (1846) carried it to the Pacific | Convention of 1818, Art. II |
| Africa split up in the late 1800s with straight lines | During the "Scramble for Africa" (Berlin Conference 1884–85 and the treaties that followed), many borders were drawn along parallels, meridians and straight lines | Herbst, *States and Power in Africa* (2000) |
| Cut through hundreds of peoples | More than 200 ethnic homelands are split by national borders | Michalopoulos & Papaioannou (2016), *American Economic Review* 106(7):1802 |
| Caprivi Strip: Germany's bid for the Zambezi | Germany got the strip in the 1890 Heligoland–Zanzibar Treaty to reach the Zambezi; Victoria Falls and the rapids below it make the river useless as a route to the Indian Ocean | Heligoland–Zanzibar Treaty (1890); *Encyclopaedia Britannica*, "Caprivi Strip" |
| Wakhan Corridor: a buffer between the empires | Set by the Durand agreement (1893) and the Anglo-Russian Pamir agreement (1895) so British India and the Russian Empire did not share a border. It is about 13 km wide at its narrowest. | Anglo-Russian Pamir Boundary Agreement (1895); *Encyclopaedia Britannica*, "Wakhan" |
| Baarle: border through cafes, gardens and homes | Baarle-Hertog (Belgium) has 22 exclaves inside the Netherlands, some with Dutch counter-exclaves inside them. They come from medieval feudal land holdings (Duke of Brabant and Lords of Breda, from the 12th century), fixed by the 1843 Treaty of Maastricht. | Municipality of Baarle-Hertog; Treaty of Maastricht (1843) |
| The front-door rule | A building split by the border is in the country where its front door is | Municipality of Baarle-Nassau / Baarle-Hertog |

## Visual notes
- **Map data:** Natural Earth 1:10m (public domain), via `python3 geo.py fetch`.
- **Straight lines in Africa:** the red lines are found from the data, not drawn by hand. The test keeps runs of a land border that stay within 0.03° of one straight chord for at least 1.5°.
- **Wakhan view:** it shows today's de facto lines, with the 1895 empires as labels.
- **Baarle:** the patchwork and the house are schematic.
