# Why Borders Are Shaped the Way They Are: script, facts, sources

Vertical Short, about 1:20, in the simple **Paper Atlas** style:
- Cream paper, pale flat countries and thin ink coastlines.
- One red line for the border each shot is about, and blue where a river draws it.
- A serif headline and a plain bold caption with the key word in red.
- Handwritten notes for the callouts.

Shot list with running times: `SHOTS.md`.

| Section | Narration |
|---|---|
| Hook | Look at a map, and borders seem random. Some wiggle, some run ruler straight, and some are just strange. But every shape has a reason. |
| Nature | The oldest borders follow nature. Rivers, like the Rio Grande, between the US and Mexico. Or mountain ridges, like the Pyrenees, between France and Spain. Easy to see, and hard to cross. |
| Straight lines | Straight lines are different. They were drawn on paper, often far from the land. In 1818, the US and Britain picked a line of latitude, the 49th parallel, across the prairies. And in the late 1800s, European empires split up Africa, with long straight lines that cut right through hundreds of peoples. |
| Deals | The strange shapes are deals. Namibia's long arm, the Caprivi Strip, was Germany's bid to reach the Zambezi River. But Victoria Falls blocks the way to the sea. And Afghanistan's thin Wakhan Corridor was left as a buffer, so the British and Russian empires would never touch. |
| Baarle | Then there's Baarle, where medieval land deals left the Belgian-Dutch border running through cafes, gardens and homes. Your house belongs to whichever country your front door is in. So every border is a story. Rivers, rulers, deals and accidents, frozen into lines. |

## Fact check

| Claim | Basis | Source |
|---|---|---|
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
