// Coffee risograph icon set: geometry for every icon on a 200 x 200 grid.
//
// Each icon has three ink layers:
//   tint - light halftone pink (secondary areas)
//   pink - solid fluorescent pink
//   blue - linework and solid blue details (default: 4px round stroke, no fill)
//
// Colour tokens are swapped at build time:
//   {T} tint, {P} pink, {B} blue
// Rules that keep the clean version correct:
//   - tint and pink shapes are plain shapes (path/rect/circle/ellipse), never <g>
//   - only shapes filled with {P} or {T} count as overlap areas
//   - blue shapes that should be solid use fill="{B}" stroke="none"

export const groups = ['Brewing', 'Drinks', 'Beans & origin', 'Café life'];

export const icons = [
  // ---------- Brewing ----------
  {
    slug: 'pour-over', name: 'Pour-over', group: 'Brewing',
    tint: [
      `<path d="M72 126 C66 148 70 168 84 178 H116 C130 168 134 148 128 126 Z" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M54 50 H146 L120 110 H80 Z" fill="{P}"/>`,
      `<circle cx="100" cy="134" r="3.5" fill="{P}"/>`,
    ],
    blue: [
      `<rect x="48" y="44" width="104" height="8" rx="2" fill="{B}" stroke="none"/>`,
      `<path d="M74 60 L88 104 M100 60 V104 M126 60 L112 104"/>`,
      `<rect x="78" y="110" width="44" height="8" rx="2" fill="{B}" stroke="none"/>`,
      `<path d="M68 123 H132"/>`,
      `<path d="M71 124 C65 148 69 168 84 178 H116 C131 168 135 148 129 124"/>`,
      `<path d="M70 152 C70 164 75 172 84 178 H116 C125 172 130 164 130 152 Z" fill="{B}" stroke="none"/>`,
      `<path d="M130 134 C146 134 148 160 127 164" stroke-width="6"/>`,
    ],
  },
  {
    slug: 'french-press', name: 'French press', group: 'Brewing',
    tint: [
      `<rect x="62" y="60" width="76" height="36" fill="{T}"/>`,
    ],
    pink: [
      `<rect x="62" y="96" width="76" height="70" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M100 50 V32"/>`,
      `<circle cx="100" cy="28" r="7" fill="{B}" stroke="none"/>`,
      `<rect x="56" y="48" width="88" height="11" rx="3" fill="{B}" stroke="none"/>`,
      `<rect x="62" y="59" width="76" height="107"/>`,
      `<path d="M62 96 H138" stroke-width="5"/>`,
      `<path d="M100 59 V96" stroke-width="3"/>`,
      `<rect x="56" y="162" width="88" height="10" rx="3" fill="{B}" stroke="none"/>`,
      `<path d="M138 72 H150 C156 72 158 76 158 82 V136 C158 142 156 146 150 146 H138" stroke-width="6"/>`,
      `<circle cx="80" cy="118" r="2.5" fill="{B}" stroke="none"/>`,
      `<circle cx="112" cy="132" r="2" fill="{B}" stroke="none"/>`,
      `<circle cx="94" cy="146" r="2.5" fill="{B}" stroke="none"/>`,
    ],
  },
  {
    slug: 'moka-pot', name: 'Moka pot', group: 'Brewing',
    tint: [
      `<path d="M70 50 H130 L124 100 H76 Z" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M76 108 H124 L134 168 H66 Z" fill="{P}"/>`,
    ],
    blue: [
      `<rect x="91" y="38" width="18" height="10" rx="3" fill="{B}" stroke="none"/>`,
      `<path d="M70 50 H130 L124 100 H76 Z"/>`,
      `<path d="M72 54 L56 44 L76 72" stroke-width="4"/>`,
      `<rect x="70" y="99" width="60" height="10" rx="2" fill="{B}" stroke="none"/>`,
      `<path d="M76 108 H124 L134 168 H66 Z"/>`,
      `<path d="M100 52 V98 M100 110 V166" stroke-width="3"/>`,
      `<path d="M128 58 H148 C152 58 154 62 152 66 L140 96 H126" stroke-width="6"/>`,
      `<path d="M84 122 L80 154 M116 122 L120 154" stroke-width="3"/>`,
    ],
  },
  {
    slug: 'gooseneck-kettle', name: 'Gooseneck kettle', group: 'Brewing',
    tint: [
      `<ellipse cx="100" cy="176" rx="56" ry="6" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M58 98 C58 80 74 70 100 70 C126 70 142 80 142 98 V156 C142 164 136 168 128 168 H72 C64 168 58 164 58 156 Z" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M58 98 C58 80 74 70 100 70 C126 70 142 80 142 98 V156 C142 164 136 168 128 168 H72 C64 168 58 164 58 156 Z"/>`,
      `<path d="M76 70 C78 57 122 57 124 70 Z" fill="{B}" stroke="none"/>`,
      `<circle cx="100" cy="54" r="5" fill="{B}" stroke="none"/>`,
      `<path d="M60 142 C40 142 34 122 38 102 C41 88 38 74 24 66" stroke-width="6"/>`,
      `<path d="M142 86 C168 86 170 142 142 148" stroke-width="7"/>`,
      `<circle cx="100" cy="118" r="13"/>`,
      `<path d="M100 118 L107 111" stroke-width="3"/>`,
      `<path d="M58 154 H142" stroke-width="3"/>`,
    ],
  },
  {
    slug: 'hand-grinder', name: 'Hand grinder', group: 'Brewing',
    tint: [
      `<path d="M64 66 H136 L130 88 H70 Z" fill="{T}"/>`,
    ],
    pink: [
      `<rect x="70" y="88" width="60" height="82" rx="8" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M100 66 V50"/>`,
      `<path d="M100 50 H150" stroke-width="6"/>`,
      `<rect x="144" y="30" width="13" height="24" rx="6.5" fill="{B}" stroke="none"/>`,
      `<circle cx="100" cy="50" r="7" fill="{B}" stroke="none"/>`,
      `<path d="M64 66 H136 L130 88 H70 Z"/>`,
      `<rect x="70" y="88" width="60" height="82" rx="8"/>`,
      `<rect x="82" y="132" width="36" height="24" rx="3"/>`,
      `<circle cx="100" cy="144" r="3.5" fill="{B}" stroke="none"/>`,
      `<ellipse cx="86" cy="77" rx="6" ry="4" transform="rotate(-20 86 77)" fill="{B}" stroke="none"/>`,
      `<ellipse cx="112" cy="78" rx="6" ry="4" transform="rotate(25 112 78)" fill="{B}" stroke="none"/>`,
      `<path d="M78 104 H122" stroke-width="3"/>`,
    ],
  },
  {
    slug: 'cold-brew-jar', name: 'Cold-brew jar', group: 'Brewing',
    tint: [
      `<ellipse cx="100" cy="176" rx="48" ry="6" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M60 86 H140 V156 A14 14 0 0 1 126 170 H74 A14 14 0 0 1 60 156 Z" fill="{P}"/>`,
    ],
    blue: [
      `<rect x="54" y="42" width="92" height="16" rx="4" fill="{B}" stroke="none"/>`,
      `<path d="M66 58 V62 M134 58 V62"/>`,
      `<rect x="60" y="62" width="80" height="108" rx="14"/>`,
      `<rect x="74" y="96" width="20" height="20" rx="2" transform="rotate(12 84 106)" stroke-width="3.5"/>`,
      `<rect x="102" y="92" width="18" height="18" rx="2" transform="rotate(-10 111 101)" stroke-width="3.5"/>`,
      `<rect x="86" y="124" width="20" height="20" rx="2" transform="rotate(6 96 134)" stroke-width="3.5"/>`,
      `<path d="M140 104 H130 M140 124 H130 M140 144 H130" stroke-width="3"/>`,
    ],
  },

  // ---------- Drinks ----------
  {
    slug: 'espresso', name: 'Espresso', group: 'Drinks',
    tint: [
      `<path d="M58 94 H142 C142 128 126 148 100 148 C74 148 58 128 58 94 Z" fill="{T}"/>`,
    ],
    pink: [
      `<ellipse cx="100" cy="153" rx="66" ry="14" fill="{P}"/>`,
      `<path d="M84 80 C76 68 92 62 84 48 M116 80 C108 68 124 62 116 48" fill="none" stroke="{P}" stroke-width="6" stroke-linecap="round"/>`,
    ],
    blue: [
      `<ellipse cx="100" cy="153" rx="66" ry="14"/>`,
      `<path d="M58 94 H142 C142 128 126 148 100 148 C74 148 58 128 58 94 Z"/>`,
      `<ellipse cx="100" cy="94" rx="42" ry="7" fill="{B}" stroke="none"/>`,
      `<path d="M141 104 C162 102 162 130 134 130" stroke-width="6"/>`,
      `<path d="M100 78 C92 64 108 58 100 42" stroke-width="6"/>`,
    ],
  },
  {
    slug: 'latte-art', name: 'Latte', group: 'Drinks',
    tint: [
      `<ellipse cx="100" cy="160" rx="68" ry="12" fill="{T}"/>`,
      `<path d="M48 86 H152 C152 128 130 154 100 154 C70 154 48 128 48 86 Z" fill="{T}"/>`,
    ],
    pink: [
      `<ellipse cx="100" cy="86" rx="52" ry="14" fill="{P}"/>`,
    ],
    blue: [
      `<path fill-rule="evenodd" d="M48 86 A52 14 0 1 0 152 86 A52 14 0 1 0 48 86 Z M100 96 C86 89 81 82 86 78 C90 75 96 77 100 82 C104 77 110 75 114 78 C119 82 114 89 100 96 Z" fill="{B}" stroke="none"/>`,
      `<path d="M48 86 C48 128 70 154 100 154 C130 154 152 128 152 86"/>`,
      `<ellipse cx="100" cy="86" rx="52" ry="14"/>`,
      `<path d="M151 98 C174 98 174 128 144 128" stroke-width="6"/>`,
      `<ellipse cx="100" cy="160" rx="68" ry="12"/>`,
    ],
  },
  {
    slug: 'cappuccino', name: 'Cappuccino', group: 'Drinks',
    tint: [
      `<path d="M56 92 C56 70 76 58 100 58 C124 58 144 70 144 92 Z" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M60 92 H140 L132 160 C131 166 126 170 120 170 H80 C74 170 69 166 68 160 Z" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M56 92 C56 70 76 58 100 58 C124 58 144 70 144 92"/>`,
      `<path d="M54 92 H146" stroke-width="5"/>`,
      `<path d="M60 92 L68 160 C69 166 74 170 80 170 H120 C126 170 131 166 132 160 L140 92"/>`,
      `<path d="M138 106 C160 106 158 140 134 142" stroke-width="6"/>`,
      `<path d="M42 174 H158"/>`,
      `<circle cx="82" cy="74" r="2" fill="{B}" stroke="none"/>`,
      `<circle cx="96" cy="68" r="2" fill="{B}" stroke="none"/>`,
      `<circle cx="110" cy="72" r="2" fill="{B}" stroke="none"/>`,
      `<circle cx="122" cy="80" r="2" fill="{B}" stroke="none"/>`,
      `<circle cx="90" cy="82" r="1.6" fill="{B}" stroke="none"/>`,
      `<circle cx="106" cy="84" r="1.6" fill="{B}" stroke="none"/>`,
      `<circle cx="72" cy="84" r="1.6" fill="{B}" stroke="none"/>`,
    ],
  },
  {
    slug: 'iced-coffee', name: 'Iced coffee', group: 'Drinks',
    tint: [
      `<path d="M63.3 72 H136.7 L135.5 90 H64.5 Z" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M64.5 90 H135.5 L130 168 H70 Z" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M126 24 L114 50 V150" stroke-width="6"/>`,
      `<path d="M62 54 H138 L130 168 H70 Z"/>`,
      `<rect x="76" y="100" width="20" height="20" rx="2" transform="rotate(10 86 110)" stroke-width="3.5"/>`,
      `<rect x="96" y="112" width="18" height="18" rx="2" transform="rotate(-8 105 121)" stroke-width="3.5"/>`,
      `<rect x="80" y="134" width="18" height="18" rx="2" transform="rotate(-4 89 143)" stroke-width="3.5"/>`,
      `<path d="M64.5 90 H135.5" stroke-width="3"/>`,
    ],
  },
  {
    slug: 'takeaway-cup', name: 'Takeaway cup', group: 'Drinks',
    tint: [
      `<path d="M66 64 H134 L124 172 H76 Z" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M69.3 100 H130.7 L127.5 134 H72.5 Z" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M66 50 C70 38 130 38 134 50"/>`,
      `<rect x="110" y="41" width="12" height="5" rx="2" fill="{B}" stroke="none"/>`,
      `<rect x="56" y="50" width="88" height="14" rx="4" fill="{B}" stroke="none"/>`,
      `<path d="M66 64 L76 172 H124 L134 64"/>`,
      `<path d="M69.3 100 H130.7 M72.5 134 H127.5" stroke-width="3"/>`,
      `<ellipse cx="100" cy="117" rx="7" ry="10" stroke-width="3"/>`,
      `<path d="M100 108 C97 114 103 120 100 126" stroke-width="2.5"/>`,
    ],
  },
  {
    slug: 'mocha', name: 'Mocha', group: 'Drinks',
    tint: [
      `<rect x="62" y="100" width="72" height="30" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M62 130 H134 V160 A10 10 0 0 1 124 170 H72 A10 10 0 0 1 62 160 Z" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M60 78 C54 66 68 56 78 62 C82 50 100 48 106 58 C114 50 134 56 130 68 C142 70 142 82 132 82 H66 C58 82 54 78 60 78 Z"/>`,
      `<path d="M72 72 Q81 64 90 72 T108 71 T126 70" stroke-width="3"/>`,
      `<path d="M62 82 V160 A10 10 0 0 0 72 170 H124 A10 10 0 0 0 134 160 V82"/>`,
      `<path d="M62 100 H134 M62 130 H134" stroke-width="3"/>`,
      `<path d="M134 94 C158 94 158 142 134 142" stroke-width="6"/>`,
    ],
  },

  // ---------- Beans & origin ----------
  {
    slug: 'coffee-bean', name: 'Coffee bean', group: 'Beans & origin',
    tint: [
      `<ellipse cx="116" cy="116" rx="46" ry="62" transform="rotate(-30 116 116)" fill="{T}"/>`,
    ],
    pink: [
      `<ellipse cx="96" cy="96" rx="46" ry="62" transform="rotate(-30 96 96)" fill="{P}"/>`,
    ],
    blue: [
      `<ellipse cx="96" cy="96" rx="46" ry="62" transform="rotate(-30 96 96)"/>`,
      `<path d="M96 36 C80 68 112 124 96 156" transform="rotate(-30 96 96)" stroke-width="6"/>`,
    ],
  },
  {
    slug: 'coffee-cherry', name: 'Coffee cherry', group: 'Beans & origin',
    tint: [
      `<path d="M122 84 C132 58 154 50 170 54 C162 72 144 88 122 84 Z" fill="{T}"/>`,
      `<path d="M66 138 C48 122 32 122 24 130 C38 146 54 148 66 138 Z" fill="{T}"/>`,
    ],
    pink: [
      `<circle cx="88" cy="130" r="12" fill="{P}"/>`,
      `<circle cx="112" cy="126" r="12" fill="{P}"/>`,
      `<circle cx="100" cy="148" r="12" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M36 164 C70 132 110 100 164 46" stroke-width="5"/>`,
      `<path d="M122 84 C132 58 154 50 170 54 C162 72 144 88 122 84 Z" stroke-width="3"/>`,
      `<path d="M126 80 C138 70 150 62 166 56" stroke-width="2.5"/>`,
      `<path d="M66 138 C48 122 32 122 24 130 C38 146 54 148 66 138 Z" stroke-width="3"/>`,
      `<path d="M62 136 C50 132 40 130 28 130" stroke-width="2.5"/>`,
      `<path d="M92 112 L90 118 M106 108 L110 114 M98 114 L100 136" stroke-width="3"/>`,
      `<path d="M78 136 A12 12 0 0 0 98 138" stroke-width="3"/>`,
      `<path d="M106 136 A12 12 0 0 0 124 128" stroke-width="3"/>`,
      `<path d="M90 156 A12 12 0 0 0 112 152" stroke-width="3"/>`,
      `<circle cx="88" cy="141" r="2" fill="{B}" stroke="none"/>`,
      `<circle cx="112" cy="137" r="2" fill="{B}" stroke="none"/>`,
      `<circle cx="100" cy="159" r="2" fill="{B}" stroke="none"/>`,
    ],
  },
  {
    slug: 'roast-bag', name: 'Roast bag', group: 'Beans & origin',
    tint: [
      `<rect x="54" y="38" width="92" height="20" rx="2" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M58 60 H142 L148 170 H52 Z" fill="{P}"/>`,
    ],
    blue: [
      `<rect x="54" y="38" width="92" height="20" rx="2" stroke-width="3"/>`,
      `<rect x="48" y="55" width="104" height="7" rx="3.5" fill="{B}" stroke="none"/>`,
      `<path d="M58 62 L52 170 H148 L142 62"/>`,
      `<circle cx="100" cy="80" r="5" stroke-width="3"/>`,
      `<rect x="74" y="96" width="52" height="54" rx="2" stroke-width="3.5"/>`,
      `<ellipse cx="100" cy="116" rx="9" ry="12" transform="rotate(-20 100 116)" stroke-width="3"/>`,
      `<path d="M101 104 C96 112 104 120 99 128" stroke-width="2.5"/>`,
      `<path d="M84 140 H116" stroke-width="3"/>`,
    ],
  },
  {
    slug: 'bean-scoop', name: 'Scoop of beans', group: 'Beans & origin',
    tint: [
      `<path d="M60 96 C64 74 84 64 100 64 C118 64 136 74 140 96 Z" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M58 96 C58 128 76 148 100 148 C124 148 142 128 142 96 Z" fill="{P}"/>`,
      `<ellipse cx="62" cy="168" rx="8" ry="5.5" transform="rotate(-20 62 168)" fill="{P}"/>`,
      `<ellipse cx="84" cy="172" rx="8" ry="5.5" transform="rotate(15 84 172)" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M58 96 H142 C142 128 124 148 100 148 C76 148 58 128 58 96 Z"/>`,
      `<path d="M140 108 L176 134" stroke-width="9"/>`,
      `<ellipse cx="80" cy="84" rx="9" ry="6" transform="rotate(-20 80 84)" stroke-width="3"/>`,
      `<ellipse cx="100" cy="74" rx="9" ry="6" transform="rotate(15 100 74)" stroke-width="3"/>`,
      `<ellipse cx="120" cy="84" rx="9" ry="6" transform="rotate(30 120 84)" stroke-width="3"/>`,
      `<path d="M72 86 L88 82 M92 72 L108 76 M113 80 L127 88" stroke-width="2"/>`,
      `<path d="M55 170 L69 166 M77 170 L91 174" stroke-width="2"/>`,
    ],
  },
  {
    slug: 'origin-pin', name: 'Origin pin', group: 'Beans & origin',
    tint: [
      `<ellipse cx="100" cy="170" rx="62" ry="13" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M100 170 C100 170 56 118 56 88 A44 44 0 0 1 144 88 C144 118 100 170 100 170 Z" fill="{P}"/>`,
    ],
    blue: [
      `<ellipse cx="100" cy="170" rx="62" ry="13" stroke-width="3"/>`,
      `<ellipse cx="100" cy="170" rx="38" ry="7" stroke-width="3"/>`,
      `<path d="M100 170 C100 170 56 118 56 88 A44 44 0 0 1 144 88 C144 118 100 170 100 170 Z"/>`,
      `<path fill-rule="evenodd" d="M79 88 A21 21 0 1 0 121 88 A21 21 0 1 0 79 88 Z M92.75 91.38 A8 11 -25 1 0 107.25 84.62 A8 11 -25 1 0 92.75 91.38 Z" fill="{B}" stroke="none"/>`,
      `<path d="M102.5 78.5 C96 86 104 91 97.5 97.5" stroke-width="2.5"/>`,
    ],
  },
  {
    slug: 'roast-gauge', name: 'Roast level', group: 'Beans & origin',
    tint: [
      `<path d="M30 140 A70 70 0 0 1 65 79.4 L77 100.2 A46 46 0 0 0 54 140 Z" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M65 79.4 A70 70 0 0 1 135 79.4 L123 100.2 A46 46 0 0 0 77 100.2 Z" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M135 79.4 A70 70 0 0 1 170 140 L146 140 A46 46 0 0 0 123 100.2 Z" fill="{B}" stroke="none"/>`,
      `<path d="M30 140 A70 70 0 0 1 170 140 M54 140 A46 46 0 0 1 146 140"/>`,
      `<path d="M100 140 L100 84" stroke-width="5"/>`,
      `<circle cx="100" cy="140" r="9" fill="{B}" stroke="none"/>`,
      `<path d="M24 140 H176"/>`,
      `<ellipse cx="42" cy="160" rx="8" ry="5.5" transform="rotate(-15 42 160)" stroke-width="3"/>`,
      `<ellipse cx="158" cy="160" rx="8" ry="5.5" transform="rotate(15 158 160)" fill="{B}" stroke="none"/>`,
    ],
  },

  // ---------- Café life ----------
  {
    slug: 'croissant', name: 'Croissant', group: 'Café life',
    tint: [
      `<ellipse cx="100" cy="154" rx="66" ry="9" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M28 128 C26 110 40 100 54 104 C58 84 78 70 100 70 C122 70 142 84 146 104 C160 100 174 110 172 128 C162 134 150 130 144 122 C132 132 116 136 100 136 C84 136 68 132 56 122 C50 130 38 134 28 128 Z" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M28 128 C26 110 40 100 54 104 C58 84 78 70 100 70 C122 70 142 84 146 104 C160 100 174 110 172 128 C162 134 150 130 144 122 C132 132 116 136 100 136 C84 136 68 132 56 122 C50 130 38 134 28 128 Z"/>`,
      `<path d="M54 104 C58 112 58 118 56 122 M78 80 C81 98 81 116 78 132 M100 72 C102 92 102 114 100 134 M122 80 C119 98 119 116 122 132 M146 104 C142 112 142 118 144 122" stroke-width="3.5"/>`,
      `<path d="M88 92 L90 96 M110 100 L112 104 M66 108 L68 112 M132 110 L134 106" stroke-width="2.5"/>`,
    ],
  },
  {
    slug: 'milk-pitcher', name: 'Milk pitcher', group: 'Café life',
    tint: [
      `<ellipse cx="102" cy="176" rx="52" ry="6" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M64 64 H130 L148 52 L136 74 C140 102 142 130 140 158 C139 165 134 170 128 170 H76 C70 170 65 165 64 158 C62 130 62 96 64 64 Z" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M64 64 H130 L148 52 L136 74 C140 102 142 130 140 158 C139 165 134 170 128 170 H76 C70 170 65 165 64 158 C62 130 62 96 64 64 Z"/>`,
      `<path d="M64 82 C38 82 38 142 64 142" stroke-width="7"/>`,
      `<path d="M118 108 H132 M122 124 H133 M118 140 H134" stroke-width="3"/>`,
      `<path d="M64 74 H134" stroke-width="3"/>`,
    ],
  },
  {
    slug: 'portafilter', name: 'Portafilter', group: 'Café life',
    tint: [
      `<path d="M66 150 H112 C112 166 102 174 89 174 C76 174 66 166 66 150 Z" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M54 80 H122 V96 C122 112 108 122 88 122 C68 122 54 112 54 96 Z" fill="{P}"/>`,
    ],
    blue: [
      `<rect x="50" y="72" width="76" height="8" rx="2" fill="{B}" stroke="none"/>`,
      `<path d="M54 80 V96 C54 112 68 122 88 122 C108 122 122 112 122 96 V80"/>`,
      `<path d="M122 84 H170 C176 84 180 88 180 94 C180 100 176 104 170 104 H122 Z" fill="{B}" stroke="none"/>`,
      `<path d="M80 122 V132 M96 122 V132" stroke-width="5"/>`,
      `<path d="M80 138 C78 141 78 143 80 144 C82 143 82 141 80 138 Z M96 140 C94 143 94 145 96 146 C98 145 98 143 96 140 Z" fill="{B}"/>`,
      `<path d="M66 150 H112 C112 166 102 174 89 174 C76 174 66 166 66 150 Z"/>`,
      `<path d="M112 154 C124 154 124 166 110 166" stroke-width="4"/>`,
    ],
  },
  {
    slug: 'stamp-card', name: 'Loyalty card', group: 'Café life',
    tint: [
      `<rect x="34" y="56" width="132" height="90" rx="8" fill="{T}"/>`,
    ],
    pink: [
      `<circle cx="62" cy="92" r="11" fill="{P}"/>`,
      `<circle cx="88" cy="92" r="11" fill="{P}"/>`,
      `<circle cx="114" cy="92" r="11" fill="{P}"/>`,
      `<circle cx="140" cy="92" r="11" fill="{P}"/>`,
      `<circle cx="62" cy="122" r="11" fill="{P}"/>`,
    ],
    blue: [
      `<rect x="34" y="56" width="132" height="90" rx="8"/>`,
      `<path d="M48 70 H98" stroke-width="4"/>`,
      `<circle cx="62" cy="92" r="11" stroke-width="3"/>`,
      `<circle cx="88" cy="92" r="11" stroke-width="3"/>`,
      `<circle cx="114" cy="92" r="11" stroke-width="3"/>`,
      `<circle cx="140" cy="92" r="11" stroke-width="3"/>`,
      `<circle cx="62" cy="122" r="11" stroke-width="3"/>`,
      `<circle cx="88" cy="122" r="11" stroke-width="3" stroke-dasharray="3 3"/>`,
      `<circle cx="114" cy="122" r="11" stroke-width="3" stroke-dasharray="3 3"/>`,
      `<path d="M140 110 L143.2 116.6 L150.5 117.7 L145.2 122.8 L146.5 130 L140 126.6 L133.5 130 L134.8 122.8 L129.5 117.7 L136.8 116.6 Z" fill="{B}" stroke="none"/>`,
      `<path d="M58 92 L61 95 L67 88 M84 92 L87 95 L93 88 M110 92 L113 95 L119 88 M136 92 L139 95 L145 88 M58 122 L61 125 L67 118" stroke-width="2.5"/>`,
    ],
  },
  {
    slug: 'storefront', name: 'Café front', group: 'Café life',
    tint: [
      `<rect x="56" y="104" width="50" height="40" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M34 60 H56 V84 A11 6 0 0 1 34 84 Z" fill="{P}"/>`,
      `<path d="M78 60 H100 V84 A11 6 0 0 1 78 84 Z" fill="{P}"/>`,
      `<path d="M122 60 H144 V84 A11 6 0 0 1 122 84 Z" fill="{P}"/>`,
      `<rect x="116" y="108" width="30" height="64" fill="{P}"/>`,
    ],
    blue: [
      `<rect x="70" y="34" width="60" height="18" rx="3" stroke-width="3.5"/>`,
      `<path d="M92 43 H108" stroke-width="3"/>`,
      `<path d="M56 60 H78 V84 A11 6 0 0 1 56 84 Z M100 60 H122 V84 A11 6 0 0 1 100 84 Z M144 60 H166 V84 A11 6 0 0 1 144 84 Z" fill="{B}" stroke="none"/>`,
      `<path d="M34 60 H166"/>`,
      `<path d="M42 90 V172 M158 90 V172"/>`,
      `<rect x="56" y="104" width="50" height="40"/>`,
      `<path d="M72 116 H90 C90 126 86 132 81 132 C76 132 72 126 72 116 Z" stroke-width="3"/>`,
      `<path d="M90 119 C96 119 96 126 89 126" stroke-width="2.5"/>`,
      `<rect x="116" y="108" width="30" height="64"/>`,
      `<circle cx="138" cy="142" r="2.5" fill="{B}" stroke="none"/>`,
      `<path d="M28 172 H172"/>`,
    ],
  },
  {
    slug: 'pickup-bell', name: 'Pickup bell', group: 'Café life',
    tint: [
      `<ellipse cx="100" cy="162" rx="66" ry="7" fill="{T}"/>`,
    ],
    pink: [
      `<path d="M50 136 C50 98 72 76 100 76 C128 76 150 98 150 136 Z" fill="{P}"/>`,
    ],
    blue: [
      `<path d="M50 136 C50 98 72 76 100 76 C128 76 150 98 150 136"/>`,
      `<rect x="36" y="134" width="128" height="13" rx="4" fill="{B}" stroke="none"/>`,
      `<rect x="95" y="62" width="10" height="16" rx="2" fill="{B}" stroke="none"/>`,
      `<circle cx="100" cy="58" r="8" fill="{B}" stroke="none"/>`,
      `<path d="M66 124 C66 106 76 94 90 88" stroke-width="4"/>`,
      `<path d="M42 72 L30 62 M42 94 L28 92 M158 72 L170 62 M158 94 L172 92" stroke-width="4"/>`,
    ],
  },
];
