/* Keel: AI SaaS dashboard kit. Vanilla JS, no build step.
   Sections: icons, helpers, data, charts, screens, shell, overlays, events. */
(function () {
  "use strict";

  /* ================= icons ================= */
  const ICONS = {
    home: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
    spark: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><path d="M12 8.5 13.2 11l2.3 1-2.3 1L12 15.5 10.8 13 8.5 12l2.3-1z"/>',
    bot: '<rect x="4" y="8" width="16" height="12" rx="3"/><path d="M12 4v4M9 13v1M15 13v1M9.5 17h5"/>',
    chart: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    card: '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19M6.5 15h3"/>',
    users: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.6-3.4 3.2-5.5 6.5-5.5s5.9 2.1 6.5 5.5"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.8c2 .7 3.2 2.5 3.5 5.2"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    layers: '<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    bell: '<path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    moon: '<path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/>',
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
    panel: '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M9 4v16"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    up: '<path d="m7 14 5-5 5 5"/>',
    down: '<path d="m7 10 5 5 5-5"/>',
    right: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    x: '<path d="M6 6l12 12M18 6 6 18"/>',
    copy: '<rect x="8" y="8" width="13" height="13" rx="2.5"/><path d="M16 8V5.5A2.5 2.5 0 0 0 13.5 3h-8A2.5 2.5 0 0 0 3 5.5v8A2.5 2.5 0 0 0 5.5 16H8"/>',
    eye: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    download: '<path d="M12 3v12M7 10l5 5 5-5M4 20h16"/>',
    play: '<path d="M7 4.5v15l12-7.5z"/>',
    more: '<circle cx="5" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="19" cy="12" r="1.2"/>',
    zap: '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    key: '<circle cx="8" cy="15" r="4.5"/><path d="m11.2 11.8 9.3-9.3M17 6l3 3M14.5 8.5l2 2"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m3.5 7 8.5 6 8.5-6"/>',
    logout: '<path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 17l-5-5 5-5M5 12h11"/>',
    file: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>',
    clip: '<path d="m20 11.5-8.2 8.2a5 5 0 0 1-7.1-7.1l8.5-8.5a3.3 3.3 0 0 1 4.7 4.7l-8.5 8.5a1.7 1.7 0 0 1-2.4-2.4l7.8-7.8"/>',
    send: '<path d="M12 19V5M6 11l6-6 6 6"/>',
    refresh: '<path d="M20 11a8 8 0 0 0-14.6-4.5L4 8M4 4v4h4M4 13a8 8 0 0 0 14.6 4.5L20 16M20 20v-4h-4"/>',
    thumb: '<path d="M7 10v11H4V10zM7 10l4-7a2.5 2.5 0 0 1 2.5 2.8L13 10h5.5a2 2 0 0 1 2 2.4l-1.4 7A2 2 0 0 1 17.1 21H7"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    alert: '<path d="M10.3 4 2.5 18a2 2 0 0 0 1.7 3h15.6a2 2 0 0 0 1.7-3L13.7 4a2 2 0 0 0-3.4 0z"/><path d="M12 9.5v4M12 17h.01"/>',
    shield: '<path d="M12 3 4.5 6v5.5c0 4.5 3.2 8.3 7.5 9.5 4.3-1.2 7.5-5 7.5-9.5V6z"/><path d="m9 12 2 2 4-4"/>',
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    filter: '<path d="M3 5h18l-7 8.5V20l-4-2v-4.5z"/>',
    chev: '<path d="m7 10 5 5 5-5"/>',
    db: '<ellipse cx="12" cy="5.5" rx="8" ry="2.5"/><path d="M4 5.5v13c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5v-13M4 12c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5"/>',
    branch: '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="7" r="2"/><path d="M6 7v10M18 9c0 5-6 4-12 8"/>',
    msg: '<path d="M4 5h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1h-9l-5 4v-4H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/>',
    code: '<path d="m8 7-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    keel: '<path d="M4 7h16l-3 6H7z"/><path d="M12 13v8M9 21h6"/>',
    trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
    edit: '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
    lock: '<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/>',
    star: '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1 6.2L12 17.3 6.5 20.2l1-6.2L3 9.6l6.2-.9z"/>'
  };
  const I = (name, size = 18, cls = "") =>
    `<svg class="icon ${cls}" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ""}</svg>`;

  /* ================= helpers ================= */
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = (n, d = 1) => {
    const a = Math.abs(n);
    if (a >= 1e9) return (n / 1e9).toFixed(d).replace(/\.0+$/, "") + "B";
    if (a >= 1e6) return (n / 1e6).toFixed(d).replace(/\.0+$/, "") + "M";
    if (a >= 1e3) return (n / 1e3).toFixed(d).replace(/\.0+$/, "") + "k";
    return String(Math.round(n));
  };
  const money = (n) => "$" + n.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function walk(n, start, drift, noise, seed) {
    const r = mulberry32(seed);
    const out = [];
    let v = start;
    for (let i = 0; i < n; i++) {
      v = Math.max(0, v + drift + (r() - 0.5) * noise);
      // gentle weekly rhythm: weekends dip
      const day = (i + 3) % 7;
      out.push(v * (day === 5 || day === 6 ? 0.82 : 1));
    }
    return out;
  }
  const TODAY = new Date(2026, 9, 31);
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function dayLabels(n) {
    const out = [];
    for (let i = n - 1; i >= 0; i--) {
      const d = new Date(TODAY);
      d.setDate(d.getDate() - i);
      out.push(`${MONTHS[d.getMonth()]} ${d.getDate()}`);
    }
    return out;
  }
  function niceMax(v) {
    if (v <= 0) return 1;
    const p = Math.pow(10, Math.floor(Math.log10(v)));
    for (const m of [1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]) if (m * p >= v) return m * p;
    return 10 * p;
  }
  const PALETTE = ["var(--c1)", "var(--c2)", "var(--c3)", "var(--c4)", "var(--c5)"];
  const AVATAR_COLORS = ["#4a5bff", "#13a36b", "#e07b39", "#b45bd6", "#0f8fb3", "#c2456b"];
  const avatar = (name, cls = "") => {
    const ini = name.split(" ").map((p) => p[0]).slice(0, 2).join("");
    const c = AVATAR_COLORS[[...name].reduce((a, ch) => a + ch.charCodeAt(0), 0) % AVATAR_COLORS.length];
    return `<span class="avatar ${cls}" style="background:${c}" title="${esc(name)}">${esc(ini)}</span>`;
  };

  /* ================= data ================= */
  const MODELS = [
    { name: "Keel Large", color: PALETTE[0], price: 12 },
    { name: "Keel Swift", color: PALETTE[1], price: 2.5 },
    { name: "Keel Vision", color: PALETTE[2], price: 9 },
    { name: "Embed v3", color: PALETTE[3], price: 0.4 }
  ];
  const AGENTS = [
    { id: "a1", name: "Support Triage", desc: "Reads incoming tickets, tags intent and drafts first replies.", icon: "msg", on: true, runs: 18420, success: 97.8, cost: 412, model: "Keel Swift" },
    { id: "a2", name: "Lead Researcher", desc: "Enriches new sign-ups with company size, stack and fit score.", icon: "search", on: true, runs: 4210, success: 94.1, cost: 286, model: "Keel Large" },
    { id: "a3", name: "Release Notes", desc: "Turns merged pull requests into a weekly changelog draft.", icon: "branch", on: true, runs: 52, success: 100, cost: 18, model: "Keel Large" },
    { id: "a4", name: "Invoice Reader", desc: "Extracts line items, totals and due dates from PDF invoices.", icon: "file", on: false, runs: 1388, success: 91.6, cost: 97, model: "Keel Vision" },
    { id: "a5", name: "SQL Copilot", desc: "Answers metric questions by writing read-only queries.", icon: "db", on: true, runs: 2905, success: 88.3, cost: 141, model: "Keel Large" },
    { id: "a6", name: "Docs Indexer", desc: "Keeps the help-center embeddings in sync with every edit.", icon: "layers", on: true, runs: 9610, success: 99.4, cost: 23, model: "Embed v3" }
  ];
  const RUNS = [
    { id: "run_8f21c", agent: "Support Triage", status: "ok", tokens: 3120, ms: 1840, when: "2 min ago" },
    { id: "run_8f21b", agent: "SQL Copilot", status: "running", tokens: 980, ms: 0, when: "3 min ago" },
    { id: "run_8f219", agent: "Lead Researcher", status: "ok", tokens: 8740, ms: 6210, when: "9 min ago" },
    { id: "run_8f214", agent: "Invoice Reader", status: "err", tokens: 1402, ms: 2950, when: "21 min ago" },
    { id: "run_8f20e", agent: "Docs Indexer", status: "ok", tokens: 22010, ms: 4120, when: "34 min ago" },
    { id: "run_8f207", agent: "Support Triage", status: "warn", tokens: 2890, ms: 9870, when: "1 h ago" }
  ];
  const TEAM = [
    { name: "Mara Okafor", email: "mara@northwind.io", role: "Owner", last: "Online", usage: 31 },
    { name: "Dev Raman", email: "dev@northwind.io", role: "Admin", last: "12 min ago", usage: 24 },
    { name: "Lena Brandt", email: "lena@northwind.io", role: "Developer", last: "1 h ago", usage: 18 },
    { name: "Tomás Ruiz", email: "tomas@northwind.io", role: "Developer", last: "Yesterday", usage: 15 },
    { name: "Aiko Sato", email: "aiko@northwind.io", role: "Analyst", last: "3 days ago", usage: 8 },
    { name: "Sam Whitfield", email: "sam@northwind.io", role: "Viewer", last: "2 weeks ago", usage: 4 }
  ];
  const INVOICES = [
    { id: "INV-2026-010", date: "Oct 1, 2026", amount: 1840, status: "Paid" },
    { id: "INV-2026-009", date: "Sep 1, 2026", amount: 1612, status: "Paid" },
    { id: "INV-2026-008", date: "Aug 1, 2026", amount: 1498, status: "Paid" },
    { id: "INV-2026-007", date: "Jul 1, 2026", amount: 1377, status: "Paid" },
    { id: "INV-2026-006", date: "Jun 1, 2026", amount: 1206, status: "Refunded" }
  ];

  const state = {
    ovRange: 30,
    usageRange: 30,
    yearly: false,
    settingsTab: "general",
    agents: AGENTS.map((a) => ({ ...a })),
    keys: [
      { name: "Production", key: "kl_live_4f9a2c7e81b0d36a5e", created: "Mar 12, 2026", used: "2 min ago", show: false },
      { name: "Staging", key: "kl_test_b72e0f19c4a85d2310", created: "Jun 3, 2026", used: "Yesterday", show: false },
      { name: "Analytics ETL", key: "kl_live_9d03e6a1f5c27b84e0", created: "Aug 28, 2026", used: "6 days ago", show: false }
    ],
    threads: [
      { id: "t1", title: "Why did support costs jump?", group: "Today", msgs: [] },
      { id: "t2", title: "Draft Q4 pricing FAQ", group: "Today", msgs: [] },
      { id: "t3", title: "Summarize churned accounts", group: "Previous 7 days", msgs: [] },
      { id: "t4", title: "Regex for invoice numbers", group: "Previous 7 days", msgs: [] }
    ],
    activeThread: null,
    streaming: false,
    flowStep: -1,
    onboardStep: 0,
    onboardChoice: "support"
  };
  // seed the first thread so the assistant screen shows a real conversation
  state.threads[0].msgs = [
    { role: "me", text: "Why did support costs jump last week?" },
    {
      role: "ai",
      blocks: [
        { p: "Support Triage spend rose 31% week over week, from $74 to $97. Two things drove it:" },
        { p: "1. Ticket volume was up 18% after the Oct 22 release, so the agent ran more often." },
        { p: "2. About 9% of runs fell back from Keel Swift to Keel Large because of long ticket threads, and Large costs roughly 5× more per token." },
        { p: "Capping thread context at 6k tokens would keep almost all runs on Swift. I estimate that saves about $20 a week with no measurable drop in reply quality." }
      ]
    }
  ];
  state.activeThread = "t1";

  /* ================= charts (hand-rolled SVG) ================= */
  function smooth(pts) {
    if (pts.length < 2) return "";
    let d = `M${pts[0][0]},${pts[0][1]}`;
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
      const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += ` C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
    }
    return d;
  }
  let gradId = 0;
  function lineChart({ labels, series, h = 260, w = 720, fmtY = fmt, unit = "" }) {
    const pl = 46, pr = 10, pt = 12, pb = 28, iw = w - pl - pr, ih = h - pt - pb, n = labels.length;
    const max = niceMax(Math.max(...series.flatMap((s) => s.values)));
    const x = (i) => pl + (n === 1 ? iw / 2 : (i * iw) / (n - 1));
    const y = (v) => pt + ih - (v / max) * ih;
    let g = "";
    for (let k = 0; k <= 4; k++) {
      const v = (max * k) / 4, yy = y(v).toFixed(1);
      g += `<line class="grid-line" x1="${pl}" x2="${w - pr}" y1="${yy}" y2="${yy}"/><text class="axis" x="${pl - 8}" y="${+yy + 4}" text-anchor="end">${fmtY(v)}${unit}</text>`;
    }
    const step = Math.ceil(n / 7);
    labels.forEach((l, i) => {
      if (i % step === 0 || i === n - 1) {
        if (i !== n - 1 && n - 1 - i < step * 0.6) return;
        g += `<text class="axis" x="${x(i)}" y="${h - 8}" text-anchor="${i === 0 ? "start" : i === n - 1 ? "end" : "middle"}">${l}</text>`;
      }
    });
    let defs = "", paths = "";
    series.forEach((s) => {
      const pts = s.values.map((v, i) => [x(i), y(v)]);
      const d = smooth(pts);
      if (s.fill) {
        const id = "g" + ++gradId;
        defs += `<linearGradient id="${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${s.color}" stop-opacity="0.22"/><stop offset="1" stop-color="${s.color}" stop-opacity="0"/></linearGradient>`;
        paths += `<path d="${d} L${x(n - 1)},${pt + ih} L${x(0)},${pt + ih} Z" fill="url(#${id})"/>`;
      }
      paths += `<path d="${d}" fill="none" stroke="${s.color}" stroke-width="${s.dash ? 1.5 : 2.25}" ${s.dash ? 'stroke-dasharray="4 4"' : ""} stroke-linecap="round"/>`;
    });
    let hits = "";
    const bw = n > 1 ? iw / (n - 1) : iw;
    labels.forEach((l, i) => {
      const tip = [l, ...series.map((s) => `${s.name}: ${fmtY(s.values[i], 2)}${unit}`)].join("|");
      hits += `<g class="hit" data-tip="${esc(tip)}"><rect class="hit-area" x="${x(i) - bw / 2}" y="${pt}" width="${bw}" height="${ih}"/><line x1="${x(i)}" x2="${x(i)}" y1="${pt}" y2="${pt + ih}"/></g>`;
    });
    return `<svg class="chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(series.map((s) => s.name).join(", "))} chart"><defs>${defs}</defs>${g}${paths}${hits}</svg>`;
  }
  function stackedBars({ labels, series, h = 260, w = 720, fmtY = fmt }) {
    const pl = 46, pr = 10, pt = 12, pb = 28, iw = w - pl - pr, ih = h - pt - pb, n = labels.length;
    const totals = labels.map((_, i) => series.reduce((a, s) => a + s.values[i], 0));
    const max = niceMax(Math.max(...totals));
    const band = iw / n, bw = Math.max(3, Math.min(26, band * 0.62));
    const y = (v) => pt + ih - (v / max) * ih;
    let g = "";
    for (let k = 0; k <= 4; k++) {
      const v = (max * k) / 4, yy = y(v).toFixed(1);
      g += `<line class="grid-line" x1="${pl}" x2="${w - pr}" y1="${yy}" y2="${yy}"/><text class="axis" x="${pl - 8}" y="${+yy + 4}" text-anchor="end">${fmtY(v)}</text>`;
    }
    const step = Math.ceil(n / 7);
    let bars = "";
    labels.forEach((l, i) => {
      const cx = pl + band * i + band / 2;
      if (i % step === 0) g += `<text class="axis" x="${cx}" y="${h - 8}" text-anchor="middle">${l}</text>`;
      let acc = 0, segs = "";
      series.forEach((s, si) => {
        const v = s.values[i], y0 = y(acc), y1 = y(acc + v);
        const top = si === series.length - 1;
        segs += `<rect class="seg-r" x="${(cx - bw / 2).toFixed(1)}" y="${y1.toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(0, y0 - y1 - (top ? 0 : 1)).toFixed(1)}" rx="${top ? 3 : 0}" fill="${s.color}"/>`;
        acc += v;
      });
      const tip = [l, ...series.map((s) => `${s.name}: ${fmtY(s.values[i], 2)}`), `Total: ${fmtY(totals[i], 2)}`].join("|");
      bars += `<g class="hit bar-hit" data-tip="${esc(tip)}"><rect class="hit-area" x="${pl + band * i}" y="${pt}" width="${band}" height="${ih}"/>${segs}</g>`;
    });
    return `<svg class="chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="Stacked bar chart">${g}${bars}</svg>`;
  }
  function donut({ items, size = 200, thick = 22, center = "", sub = "" }) {
    const r = (size - 30) / 2, C = 2 * Math.PI * r, total = items.reduce((a, b) => a + b.value, 0);
    let acc = 0, segs = "";
    items.forEach((it) => {
      const len = (it.value / total) * C;
      const gap = items.length > 1 ? 3 : 0;
      segs += `<circle class="donut-seg" data-tip="${esc(`${it.name}|${money(it.value)} · ${((it.value / total) * 100).toFixed(1)}%`)}" cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="${it.color}" stroke-width="${thick}" stroke-dasharray="${Math.max(0, len - gap)} ${C}" stroke-dashoffset="${-acc}" transform="rotate(-90 ${size / 2} ${size / 2})"/>`;
      acc += len;
    });
    return `<svg class="chart" viewBox="0 0 ${size} ${size}" style="max-width:${size}px;margin:0 auto" role="img" aria-label="Donut chart">${segs}<text x="50%" y="48%" text-anchor="middle" font-size="22" font-weight="600" fill="var(--text)" style="letter-spacing:-.02em">${center}</text><text x="50%" y="60%" text-anchor="middle" font-size="11" fill="var(--text-3)">${sub}</text></svg>`;
  }
  function sparkline(values, color = "var(--accent)", w = 110, h = 34) {
    const max = Math.max(...values), min = Math.min(...values), n = values.length;
    const pts = values.map((v, i) => [(i * w) / (n - 1), h - 3 - ((v - min) / (max - min || 1)) * (h - 6)]);
    const d = smooth(pts);
    const id = "s" + ++gradId;
    return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" aria-hidden="true"><defs><linearGradient id="${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${color}" stop-opacity=".25"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs><path d="${d} L${w},${h} L0,${h} Z" fill="url(#${id})"/><path d="${d}" fill="none" stroke="${color}" stroke-width="1.75"/></svg>`;
  }
  const legend = (series) => `<div class="legend">${series.map((s) => `<span><i style="background:${s.color}"></i>${esc(s.name)}</span>`).join("")}</div>`;

  /* ================= shared bits ================= */
  const pageHead = (title, sub, actions = "") =>
    `<div class="page-head"><div><h1>${title}</h1>${sub ? `<p>${sub}</p>` : ""}</div><div class="head-actions">${actions}</div></div>`;
  const seg = (name, opts, cur) =>
    `<div class="seg" role="tablist">${opts.map(([v, l]) => `<button role="tab" aria-selected="${v === cur}" class="${v === cur ? "on" : ""}" data-action="seg" data-name="${name}" data-value="${v}">${l}</button>`).join("")}</div>`;
  const statusBadge = (s) =>
    ({ ok: '<span class="badge ok dot">Succeeded</span>', running: '<span class="badge info dot">Running</span>', err: '<span class="badge err dot">Failed</span>', warn: '<span class="badge warn dot">Slow</span>' }[s]);
  function kpi({ label, value, delta, good, spark, color, foot }) {
    const up = delta >= 0;
    return `<div class="card kpi">
      <div class="kpi-top"><span>${label}</span>${I("more", 16, "faint")}</div>
      <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:8px"><div class="kpi-val">${value}</div>${sparkline(spark, color)}</div>
      <div class="kpi-foot"><span class="delta ${good ? "up" : "down"}">${I(up ? "up" : "down", 13)}${Math.abs(delta).toFixed(1)}%</span><span>${foot}</span></div>
    </div>`;
  }

  /* ================= screens ================= */
  const screens = {};

  screens.overview = () => {
    const n = state.ovRange;
    const labels = dayLabels(n);
    const req = walk(n, 38000, 420, 9000, 11 + n);
    const prev = walk(n, 33000, 300, 8000, 29 + n);
    const usageShare = [
      { ...MODELS[0], v: 46 }, { ...MODELS[1], v: 31 }, { ...MODELS[2], v: 15 }, { ...MODELS[3], v: 8 }
    ];
    return `
      ${pageHead("Good evening, Mara", "Here’s what your AI workspace did over the last " + n + " days.",
        `<button class="btn" data-action="toast" data-msg="Report exported as CSV">${I("download", 16)}Export</button>
         <button class="btn primary" data-action="go" data-route="assistant">${I("spark", 16)}Ask Keel</button>`)}
      <div class="grid g-4">
        ${kpi({ label: "Monthly recurring revenue", value: "$61.8k", delta: 8.2, good: true, spark: walk(16, 50, 0.8, 4, 3), color: "var(--c1)", foot: "vs. last month" })}
        ${kpi({ label: "Active users", value: "12,480", delta: 4.1, good: true, spark: walk(16, 50, 0.4, 5, 4), color: "var(--c2)", foot: "7-day average" })}
        ${kpi({ label: "Tokens processed", value: "1.92B", delta: 18.6, good: true, spark: walk(16, 50, 1.4, 6, 5), color: "var(--c4)", foot: "this period" })}
        ${kpi({ label: "p95 latency", value: "842ms", delta: -6.3, good: true, spark: walk(16, 50, -0.6, 5, 6), color: "var(--c3)", foot: "lower is better" })}
      </div>
      <div class="grid g-main mt">
        <div class="card">
          <div class="card-head"><div><h3>API requests</h3><div class="sub">${fmt(req.reduce((a, b) => a + b, 0))} requests · dashed line is the previous period</div></div>
            ${seg("ovRange", [[7, "7D"], [30, "30D"], [90, "90D"]], n)}</div>
          <div class="card-body">
            ${legend([{ name: "This period", color: "var(--c1)" }, { name: "Previous period", color: "var(--c5)" }])}
            <div class="chart-wrap" style="margin-top:12px">${lineChart({ labels, series: [{ name: "Requests", values: req, color: "var(--c1)", fill: true }, { name: "Previous", values: prev, color: "var(--c5)", dash: true }] })}</div>
          </div>
        </div>
        <div class="card insight">
          <div class="card-body" style="display:grid;gap:12px">
            <div style="display:flex;align-items:center;gap:10px"><span class="spark-ic">${I("spark", 18)}</span><div><b>Keel summary</b><div class="faint" style="font-size:12.5px">Generated 4 min ago from your workspace</div></div></div>
            <ul>
              <li><span><b>Requests are up 21%</b>, mostly from the Support Triage agent after the Oct 22 release.</span></li>
              <li><span><b>Invoice Reader failed 14 times</b> on scanned PDFs. Turning on OCR pre-processing should fix most of them.</span></li>
              <li><span><b>You’re at 78% of your token quota</b> with 9 days left. At this pace you’ll hit it on Nov 7.</span></li>
            </ul>
            <div style="display:flex;gap:8px;flex-wrap:wrap">
              <button class="btn accent sm" data-action="ask" data-prompt="Why did Invoice Reader fail on scanned PDFs?">Ask a follow-up</button>
              <button class="btn ghost sm" data-action="toast" data-msg="Summary regenerated">${I("refresh", 14)}Regenerate</button>
            </div>
          </div>
        </div>
      </div>
      <div class="grid g-main mt">
        <div class="card">
          <div class="card-head"><div><h3>Recent agent runs</h3><div class="sub">Live from the last hour</div></div><button class="btn sm" data-action="go" data-route="agents">View all ${I("right", 14)}</button></div>
          <div class="table-wrap" style="margin-top:14px"><table class="table">
            <thead><tr><th>Run</th><th>Agent</th><th>Status</th><th class="r">Tokens</th><th class="r">Duration</th><th class="r">Started</th></tr></thead>
            <tbody>${RUNS.map((r) => `<tr><td class="mono faint">${r.id}</td><td>${r.agent}</td><td>${statusBadge(r.status)}</td><td class="r num">${r.tokens.toLocaleString()}</td><td class="r num">${r.ms ? (r.ms / 1000).toFixed(2) + "s" : "…"}</td><td class="r faint">${r.when}</td></tr>`).join("")}</tbody>
          </table></div>
        </div>
        <div class="card">
          <div class="card-head"><div><h3>Usage by model</h3><div class="sub">Share of tokens</div></div></div>
          <div class="card-body">
            ${usageShare.map((m) => `<div class="hbar"><div class="hbar-top"><span><i style="background:${m.color}"></i>${m.name}</span><span class="num muted">${m.v}%</span></div><div class="bar"><i style="width:${m.v}%;background:${m.color}"></i></div></div>`).join("")}
            <div class="alert info" style="margin-top:14px">${I("zap", 18)}<div><b>Routing tip</b><span class="muted">Moving SQL Copilot to Keel Swift could save about $60 a month.</span></div></div>
          </div>
        </div>
      </div>`;
  };

  /* ---------- assistant ---------- */
  const CANNED = [
    {
      match: /invoice|pdf|scan|ocr/i,
      blocks: [
        { p: "14 of the 1,388 Invoice Reader runs failed this month. 12 of those were scanned PDFs with no text layer, so the model only got low-resolution page images." },
        { p: "Turn on OCR before extraction in the agent’s input step:" },
        { code: 'steps:\n  - type: ocr\n    engine: fast\n    when: "pdf.text_layer == false"\n  - type: extract\n    model: keel-vision' },
        { p: "This adds about 300 ms per scanned file and should recover most of those failures." }
      ]
    },
    {
      match: /regex|pattern/i,
      blocks: [
        { p: "This matches invoice numbers like INV-2026-010 and gives you the year and sequence as separate groups:" },
        { code: "/\\bINV-(\\d{4})-(\\d{3,})\\b/g" },
        { p: "Group 1 is the year and group 2 is the sequence number. Drop the \\b anchors if the numbers can sit inside other text." }
      ]
    },
    {
      match: /churn/i,
      blocks: [
        { p: "23 accounts churned in October, $4.1k MRR in total. Three patterns stand out:" },
        { p: "• 11 never connected a second data source in their first 14 days.\n• 7 hit rate limits on the Starter plan and left within a week.\n• 5 named price as the reason in the exit survey, all on annual plans up for renewal." },
        { p: "The quickest win is probably a nudge on day 3 to connect a second source." }
      ]
    }
  ];
  const DEFAULT_REPLY = (q) => [
    { p: `Here’s a first pass at “${q.length > 80 ? q.slice(0, 80) + "…" : q}”.` },
    { p: "I looked at the last 30 days of workspace data: 1.92B tokens across 6 agents and 4 models. Nothing unusual stands out for this question, but I can dig into any agent, model or date range if you narrow it down." },
    { p: "Try asking for a comparison, like “Swift vs Large cost for Support Triage”, or a forecast, like “when will we hit our quota?”" }
  ];
  const renderBlocks = (blocks, words) => {
    let left = words === undefined ? Infinity : words;
    let html = "";
    for (const b of blocks) {
      if (left <= 0) break;
      const text = b.p ?? b.code;
      const parts = text.split(/(\s+)/);
      let out = "";
      for (const part of parts) {
        if (left <= 0) break;
        out += part;
        if (part.trim()) left--;
      }
      html += b.code ? `<pre><code>${esc(out)}</code></pre>` : `<p style="white-space:pre-line">${esc(out)}</p>`;
    }
    return html;
  };
  const countWords = (blocks) => blocks.reduce((a, b) => a + (b.p ?? b.code).split(/\s+/).filter(Boolean).length, 0);
  function renderMessages() {
    const t = state.threads.find((x) => x.id === state.activeThread);
    if (!t || !t.msgs.length) {
      return `<div class="empty-chat">
        <span class="spark-ic" style="width:44px;height:44px;border-radius:12px;display:grid;place-items:center;background:var(--accent);color:var(--accent-ink)">${I("spark", 22)}</span>
        <h2>What should we look into?</h2>
        <p class="muted" style="margin:0">Keel can read your metrics, agents and billing. Ask it anything about your workspace.</p>
        <div class="prompt-grid">
          ${[["Explain a spike", "Why did support costs jump?"], ["Fix failures", "Why did Invoice Reader fail on scanned PDFs?"], ["Find patterns", "Summarize churned accounts this month"], ["Write code", "Regex for invoice numbers like INV-2026-010"]]
            .map(([t2, p]) => `<button class="prompt-card" data-action="ask" data-prompt="${esc(p)}"><b>${t2}</b>${esc(p)}</button>`).join("")}
        </div></div>`;
    }
    return t.msgs.map((m) => m.role === "me"
      ? `<div class="msg me"><div class="bubble">${esc(m.text)}</div></div>`
      : `<div class="msg ai"><span class="who">${I("spark", 16)}</span><div class="bubble">${renderBlocks(m.blocks, m.words)}${m.words !== undefined ? '<span class="cursor"></span>' : `<div class="msg-tools"><button class="btn ghost sm icon-only" data-action="copy-msg" aria-label="Copy">${I("copy", 15)}</button><button class="btn ghost sm icon-only" data-action="toast" data-msg="Thanks for the feedback" aria-label="Good answer">${I("thumb", 15)}</button><button class="btn ghost sm icon-only" data-action="toast" data-msg="Regenerating…" aria-label="Regenerate">${I("refresh", 15)}</button></div>`}</div></div>`).join("");
  }
  screens.assistant = () => {
    const groups = {};
    state.threads.forEach((t) => (groups[t.group] = groups[t.group] || []).push(t));
    const t = state.threads.find((x) => x.id === state.activeThread);
    return `<div class="card chat-shell">
      <aside class="threads">
        <button class="btn primary" data-action="new-chat" style="margin-bottom:6px">${I("plus", 16)}New chat</button>
        ${Object.entries(groups).map(([g, ts]) => `<h4>${g}</h4>${ts.map((x) => `<button class="thread ${x.id === state.activeThread ? "on" : ""}" data-action="thread" data-id="${x.id}">${esc(x.title)}</button>`).join("")}`).join("")}
      </aside>
      <section class="convo">
        <div class="convo-head"><div style="min-width:0"><b style="display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${t && t.msgs.length ? esc(t.title) : "New chat"}</b><span class="faint" style="font-size:12.5px">Workspace context on · 6 agents · 4 data sources</span></div>
          <div style="display:flex;gap:6px"><button class="btn sm only-mobile" data-action="new-chat">${I("plus", 14)}</button><button class="btn sm" data-action="toast" data-msg="Share link copied">Share</button></div></div>
        <div class="messages" id="messages">${renderMessages()}</div>
        <div class="composer-wrap">
          <form class="composer" data-form="chat">
            <label class="sr-only" for="prompt">Message Keel</label>
            <textarea id="prompt" rows="1" placeholder="Ask about usage, agents, costs…"></textarea>
            <div class="composer-bar">
              <button type="button" class="btn ghost sm icon-only" data-action="toast" data-msg="File picker would open here" aria-label="Attach file">${I("clip", 16)}</button>
              <select class="select" aria-label="Model">${MODELS.slice(0, 3).map((m) => `<option>${m.name}</option>`).join("")}</select>
              <span class="faint hide-mobile" style="font-size:12px;margin-left:4px"><kbd>Enter</kbd> to send · <kbd>Shift</kbd>+<kbd>Enter</kbd> for a new line</span>
              <button class="btn accent sm icon-only" style="margin-left:auto" type="submit" aria-label="Send" ${state.streaming ? "disabled" : ""}>${I("send", 16)}</button>
            </div>
          </form>
        </div>
      </section>
    </div>`;
  };
  function ask(q) {
    q = q.trim();
    if (!q || state.streaming) return;
    let t = state.threads.find((x) => x.id === state.activeThread);
    if (!t) {
      t = { id: "t" + Date.now(), title: q.slice(0, 48), group: "Today", msgs: [] };
      state.threads.unshift(t);
      state.activeThread = t.id;
    }
    if (!t.msgs.length) t.title = q.slice(0, 48);
    t.msgs.push({ role: "me", text: q });
    const hit = CANNED.find((c) => c.match.test(q));
    const reply = { role: "ai", blocks: hit ? hit.blocks : DEFAULT_REPLY(q), words: 0 };
    t.msgs.push(reply);
    state.streaming = true;
    if (route() !== "assistant") location.hash = "#/assistant";
    else render();
    const total = countWords(reply.blocks);
    const tick = () => {
      reply.words += 1 + Math.floor(Math.random() * 3);
      if (reply.words >= total) { delete reply.words; state.streaming = false; }
      const box = $("#messages");
      if (box) { box.innerHTML = renderMessages(); box.scrollTop = box.scrollHeight; }
      if (state.streaming) setTimeout(tick, 40);
      else { const b = $('.composer button[type="submit"]'); if (b) b.disabled = false; }
    };
    setTimeout(tick, 380);
  }

  /* ---------- agents ---------- */
  const FLOW = [
    { kind: "Trigger", name: "New ticket in inbox", icon: "mail" },
    { kind: "Classify", name: "Intent + urgency", icon: "filter" },
    { kind: "Retrieve", name: "Help-center search", icon: "db" },
    { kind: "Generate", name: "Draft reply · Swift", icon: "spark" },
    { kind: "Review", name: "Confidence ≥ 0.82?", icon: "shield" },
    { kind: "Action", name: "Send or hand off", icon: "right" }
  ];
  const flowHtml = () => FLOW.map((f, i) => {
    const s = state.flowStep;
    const st = s === -1 ? "" : i < s ? "done" : i === s ? "running" : "";
    return `${i ? `<div class="flow-link ${s >= i ? "live" : ""}"></div>` : ""}<div class="flow-node ${st}"><small>${f.kind}</small><div style="display:flex;align-items:center;gap:8px">${I(f.icon, 16, "muted")}<b>${f.name}</b></div><span>${st === "done" ? '<span class="badge ok">Done</span>' : st === "running" ? '<span class="badge info dot">Running</span>' : '<span class="badge">Idle</span>'}</span></div>`;
  }).join("");
  screens.agents = () => {
    const live = state.agents.filter((a) => a.on).length;
    return `${pageHead("Agents", `${live} of ${state.agents.length} agents are live. Each runs on its own trigger and budget.`,
      `<button class="btn" data-action="toast" data-msg="Opened run logs">${I("file", 16)}Logs</button><button class="btn primary" data-action="modal" data-modal="agent">${I("plus", 16)}New agent</button>`)}
    <div class="card"><div class="card-head"><div><h3>Workflow · Support Triage</h3><div class="sub">Step through a sample run to see how a ticket moves</div></div>
      <button class="btn sm" data-action="run-flow" ${state.flowStep >= 0 && state.flowStep < FLOW.length ? "disabled" : ""}>${I("play", 14)}Test run</button></div>
      <div class="card-body"><div class="flow" id="flow">${flowHtml()}</div></div></div>
    <div class="grid g-3 mt">${state.agents.map((a) => `<div class="card agent-card">
      <div class="agent-top"><span class="tile-ic">${I(a.icon, 20)}</span><div style="flex:1;min-width:0"><h3>${a.name}</h3><p>${a.desc}</p></div>
        <label class="switch" title="${a.on ? "Pause" : "Activate"} agent"><input type="checkbox" data-action="toggle-agent" data-id="${a.id}" ${a.on ? "checked" : ""} aria-label="${a.name} active"><span></span></label></div>
      <div style="display:flex;gap:6px;flex-wrap:wrap">${a.on ? '<span class="badge ok dot">Live</span>' : '<span class="badge dot">Paused</span>'}<span class="badge outline">${a.model}</span></div>
      <div class="agent-stats"><div><small>Runs</small><b>${fmt(a.runs)}</b></div><div><small>Success</small><b>${a.success}%</b></div><div><small>Cost / mo</small><b>${money(a.cost)}</b></div></div>
    </div>`).join("")}</div>`;
  };
  function runFlow() {
    state.flowStep = 0;
    const step = () => {
      const el = $("#flow");
      if (!el) { state.flowStep = -1; return; }
      el.innerHTML = flowHtml();
      if (state.flowStep < FLOW.length) { state.flowStep++; setTimeout(step, 700); }
      else { toast("Test run finished. Reply drafted in 3.1s"); const b = $('[data-action="run-flow"]'); if (b) b.disabled = false; }
    };
    const b = $('[data-action="run-flow"]'); if (b) b.disabled = true;
    step();
  }

  /* ---------- usage ---------- */
  screens.usage = () => {
    const n = state.usageRange, labels = dayLabels(n);
    const series = MODELS.map((m, i) => ({ name: m.name, color: m.color, values: walk(n, [26, 18, 9, 5][i] * 1e6, [0.2, 0.15, 0.05, 0.02][i] * 1e6, [8, 6, 4, 2][i] * 1e6, 70 + i + n) }));
    const p50 = walk(n, 380, -1, 60, 91 + n), p95 = p50.map((v, i) => v * 2.1 + ((i * 37) % 90));
    const costs = MODELS.map((m, i) => ({ name: m.name, color: m.color, value: Math.round(series[i].values.reduce((a, b) => a + b, 0) / 1e6 * m.price / 4) }));
    const totalTok = series.reduce((a, s) => a + s.values.reduce((x, y) => x + y, 0), 0);
    const totalCost = costs.reduce((a, c) => a + c.value, 0);
    return `${pageHead("Usage", "Tokens, cost and latency across every model and API key.",
      `${seg("usageRange", [[7, "7D"], [30, "30D"], [90, "90D"]], n)}<button class="btn">${I("filter", 16)}All keys</button>`)}
    <div class="grid g-4">
      <div class="card kpi"><div class="kpi-top">Total tokens</div><div class="kpi-val">${fmt(totalTok, 2)}</div><div class="kpi-foot">across ${MODELS.length} models</div></div>
      <div class="card kpi"><div class="kpi-top">Spend</div><div class="kpi-val">${money(totalCost)}</div><div class="kpi-foot">${money(Math.round(totalCost / n))} per day on average</div></div>
      <div class="card kpi"><div class="kpi-top">Requests</div><div class="kpi-val">${fmt(totalTok / 1180, 1)}</div><div class="kpi-foot">about 1,180 tokens each</div></div>
      <div class="card kpi"><div class="kpi-top">Error rate</div><div class="kpi-val">0.42%</div><div class="kpi-foot"><span class="delta up">${I("down", 13)}0.1%</span><span>vs. previous period</span></div></div>
    </div>
    <div class="grid g-main mt">
      <div class="card"><div class="card-head"><div><h3>Tokens per day</h3><div class="sub">Stacked by model</div></div>${legend(series)}</div>
        <div class="card-body">${stackedBars({ labels, series })}</div></div>
      <div class="card"><div class="card-head"><div><h3>Cost by model</h3><div class="sub">Hover a segment</div></div></div>
        <div class="card-body">${donut({ items: costs, center: money(totalCost), sub: `last ${n} days` })}
          <div class="list" style="margin-top:12px">${costs.map((c) => `<div class="list-row" style="padding:8px 0"><i style="width:8px;height:8px;border-radius:2px;background:${c.color}"></i><span class="grow">${c.name}</span><b class="num">${money(c.value)}</b></div>`).join("")}</div></div></div>
    </div>
    <div class="grid g-2 mt">
      <div class="card"><div class="card-head"><div><h3>Latency</h3><div class="sub">Milliseconds to first token</div></div>${legend([{ name: "p50", color: "var(--c2)" }, { name: "p95", color: "var(--c3)" }])}</div>
        <div class="card-body">${lineChart({ labels, h: 230, series: [{ name: "p50", values: p50, color: "var(--c2)" }, { name: "p95", values: p95, color: "var(--c3)" }], fmtY: (v) => Math.round(v), unit: "ms" })}</div></div>
      <div class="card"><div class="card-head"><div><h3>Top API keys</h3><div class="sub">By spend this period</div></div></div>
        <div class="table-wrap" style="margin-top:14px"><table class="table"><thead><tr><th>Key</th><th class="r">Requests</th><th class="r">Spend</th><th>Budget</th></tr></thead><tbody>
        ${[["Production", 0.62, 0.81], ["Analytics ETL", 0.21, 0.44], ["Staging", 0.12, 0.92], ["Personal · Dev", 0.05, 0.18]].map(([k, share, b]) => `<tr><td><div class="cell-user">${I("key", 16, "faint")}<span>${k}</span></div></td><td class="r num">${fmt((totalTok / 1180) * share)}</td><td class="r num">${money(Math.round(totalCost * share))}</td><td style="min-width:120px"><div class="bar ${b > 0.9 ? "warn" : ""}"><i style="width:${b * 100}%"></i></div></td></tr>`).join("")}
        </tbody></table></div></div>
    </div>`;
  };

  /* ---------- billing ---------- */
  const PLANS = [
    { name: "Starter", m: 0, desc: "For trying things out", feats: ["1M tokens / month", "2 agents", "Community support"] },
    { name: "Team", m: 49, desc: "For small product teams", feats: ["50M tokens / month", "Unlimited agents", "Usage alerts", "Email support"], current: true },
    { name: "Scale", m: 199, desc: "For production workloads", feats: ["400M tokens / month", "SSO and audit log", "Dedicated throughput", "99.9% uptime SLA"] }
  ];
  screens.billing = () => `${pageHead("Billing", "Manage your plan, payment method and invoices.")}
    <div class="grid g-main">
      <div class="card card-pad" style="display:grid;gap:18px">
        <div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:flex-start">
          <div><span class="badge info">Current plan</span><h2 style="margin:8px 0 2px;font-size:22px;letter-spacing:-.02em">Team · $49 per seat</h2><span class="muted">6 seats · renews Nov 1, 2026 · next invoice about ${money(1912)}</span></div>
          <div class="head-actions"><button class="btn" data-action="toast" data-msg="Billing portal would open here">Manage</button><button class="btn primary" data-action="go" data-route="billing" data-scroll="plans">Upgrade</button></div>
        </div>
        <div class="grid g-3">
          ${[["Tokens", "39.2M of 50M", 78, "warn"], ["Seats", "6 of 10", 60, ""], ["Agents", "6 of unlimited", 12, "ok"]].map(([k, v, p, c]) => `<div style="display:grid;gap:8px"><div style="display:flex;justify-content:space-between;font-size:13px"><span class="muted">${k}</span><span class="num">${v}</span></div><div class="bar ${c}"><i style="width:${p}%"></i></div></div>`).join("")}
        </div>
        <div class="alert warn">${I("alert", 18)}<div><b>You’re on track to use 112% of your tokens</b><span class="muted">Overage is billed at $1.20 per 1M tokens. Turn on auto-upgrade to avoid throttling.</span></div></div>
      </div>
      <div class="card card-pad" style="display:grid;gap:14px;align-content:start">
        <h3 style="margin:0;font-size:14.5px">Payment method</h3>
        <div style="border-radius:14px;padding:18px;color:#fff;background:linear-gradient(135deg,#1c1d2b,#3a3f8f 60%,#7d8aff);display:grid;gap:22px">
          <div style="display:flex;justify-content:space-between">${I("keel", 22)}<span style="font-size:12px;opacity:.8">Business debit</span></div>
          <div class="mono" style="font-size:16px;letter-spacing:.12em">•••• •••• •••• 4821</div>
          <div style="display:flex;justify-content:space-between;font-size:12.5px;opacity:.85"><span>NORTHWIND LABS</span><span>09 / 29</span></div>
        </div>
        <button class="btn" data-action="toast" data-msg="Card form would open here">Replace card</button>
      </div>
    </div>
    <div class="page-head" id="plans" style="margin:28px 0 14px"><div><h1 style="font-size:18px">Plans</h1></div>${seg("yearly", [["0", "Monthly"], ["1", "Yearly · save 20%"]], state.yearly ? "1" : "0")}</div>
    <div class="grid g-3">${PLANS.map((p) => {
      const price = state.yearly ? Math.round(p.m * 0.8) : p.m;
      return `<div class="card plan ${p.current ? "current" : ""}">${p.current ? '<span class="badge info tag">Current</span>' : p.name === "Scale" ? '<span class="badge outline tag">Most popular</span>' : ""}
        <div><h3>${p.name}</h3><span class="muted">${p.desc}</span></div>
        <div class="price">$${price}<small> / seat / month${state.yearly && p.m ? ", billed yearly" : ""}</small></div>
        <ul>${p.feats.map((f) => `<li>${I("check", 16)}${f}</li>`).join("")}</ul>
        <button class="btn ${p.current ? "" : p.name === "Scale" ? "primary" : ""}" ${p.current ? "disabled" : ""} data-action="toast" data-msg="Switched to ${p.name}. Changes apply at the next billing cycle">${p.current ? "Your plan" : p.m > 49 ? "Upgrade to " + p.name : "Downgrade"}</button></div>`;
    }).join("")}</div>
    <div class="card mt"><div class="card-head"><div><h3>Invoices</h3><div class="sub">Sent to billing@northwind.io</div></div></div>
      <div class="table-wrap" style="margin-top:14px"><table class="table"><thead><tr><th>Invoice</th><th>Date</th><th>Status</th><th class="r">Amount</th><th class="r"></th></tr></thead><tbody>
      ${INVOICES.map((v) => `<tr><td class="mono">${v.id}</td><td class="muted">${v.date}</td><td>${v.status === "Paid" ? '<span class="badge ok">Paid</span>' : '<span class="badge">Refunded</span>'}</td><td class="r num">${money(v.amount)}</td><td class="r"><button class="btn ghost sm" data-action="toast" data-msg="Downloading ${v.id}.pdf">${I("download", 14)}PDF</button></td></tr>`).join("")}
      </tbody></table></div></div>`;

  /* ---------- team ---------- */
  screens.team = () => `${pageHead("Team", "People with access to the Northwind Labs workspace.",
    `<button class="btn primary" data-action="modal" data-modal="invite">${I("plus", 16)}Invite people</button>`)}
    <div class="grid g-4">
      <div class="card kpi"><div class="kpi-top">Members</div><div class="kpi-val">6</div><div class="kpi-foot">4 seats left</div></div>
      <div class="card kpi"><div class="kpi-top">Pending invites</div><div class="kpi-val">2</div><div class="kpi-foot">expire in 7 days</div></div>
      <div class="card kpi"><div class="kpi-top">Active this week</div><div class="kpi-val">5</div><div class="avatars">${TEAM.slice(0, 5).map((t) => avatar(t.name)).join("")}</div></div>
      <div class="card kpi"><div class="kpi-top">SSO</div><div class="kpi-val" style="font-size:20px;padding:6px 0">Not set up</div><div class="kpi-foot"><a href="#/billing" style="color:var(--accent)">Available on Scale →</a></div></div>
    </div>
    <div class="card mt"><div class="card-head"><div class="input-group" style="width:100%;max-width:300px">${I("search", 16)}<input class="input" placeholder="Search members" data-filter="team" aria-label="Search members"></div></div>
      <div class="table-wrap" style="margin-top:14px"><table class="table"><thead><tr><th>Member</th><th>Role</th><th>Share of usage</th><th>Last active</th><th class="r"></th></tr></thead><tbody id="team-body">
      ${TEAM.map((t) => `<tr data-name="${esc(t.name.toLowerCase() + " " + t.email)}"><td><div class="cell-user">${avatar(t.name)}<div>${t.name}<small>${t.email}</small></div></div></td>
        <td>${t.role === "Owner" ? '<span class="badge">Owner</span>' : `<select class="select" style="height:30px;width:auto;font-size:13px" data-action="role" data-name="${esc(t.name)}" aria-label="Role for ${esc(t.name)}">${["Admin", "Developer", "Analyst", "Viewer"].map((r) => `<option ${r === t.role ? "selected" : ""}>${r}</option>`).join("")}</select>`}</td>
        <td style="min-width:140px"><div style="display:flex;align-items:center;gap:10px"><div class="bar" style="flex:1"><i style="width:${t.usage * 3}%"></i></div><span class="num faint" style="font-size:12px">${t.usage}%</span></div></td>
        <td class="${t.last === "Online" ? "" : "muted"}">${t.last === "Online" ? '<span class="badge ok dot">Online</span>' : t.last}</td>
        <td class="r"><button class="btn ghost sm icon-only" aria-label="More" data-action="toast" data-msg="Member actions menu">${I("more", 16)}</button></td></tr>`).join("")}
      </tbody></table></div></div>`;

  /* ---------- settings ---------- */
  const settingsTabs = { general: "General", keys: "API keys", notifications: "Notifications", security: "Security" };
  const row = (title, desc, body) => `<div class="settings-row"><div><h4>${title}</h4><p>${desc}</p></div><div style="display:grid;gap:12px;align-content:start">${body}</div></div>`;
  const toggleRow = (label, sub, on) => `<label style="display:flex;align-items:center;justify-content:space-between;gap:16px;cursor:pointer"><span>${label}<small class="faint" style="display:block">${sub}</small></span><span class="switch"><input type="checkbox" ${on ? "checked" : ""} data-action="toast-toggle" data-label="${esc(label)}"><span></span></span></label>`;
  screens.settings = () => {
    const tab = state.settingsTab;
    let body = "";
    if (tab === "general") body =
      row("Workspace", "Shown to your team and on invoices.", `<div class="field"><label for="ws-name">Name</label><input id="ws-name" class="input" value="Northwind Labs"></div><div class="field"><label for="ws-url">Workspace URL</label><div class="input-group">${I("globe", 16)}<input id="ws-url" class="input" value="northwind.keel.app"></div></div>`) +
      row("Default model", "Used by new agents and the assistant unless you pick another.", `<select class="select">${MODELS.slice(0, 3).map((m) => `<option>${m.name}</option>`).join("")}</select><div class="field"><label>Creativity · <span class="num" id="temp-val">0.4</span></label><input type="range" class="range" min="0" max="1" step="0.1" value="0.4" data-action="temp" aria-label="Temperature"></div>`) +
      row("Data retention", "How long prompts and outputs are kept for logs and evals.", `<div class="seg">${["7 days", "30 days", "90 days", "Forever"].map((d, i) => `<button class="${i === 1 ? "on" : ""}" data-action="seg-local">${d}</button>`).join("")}</div>`) +
      row("Danger zone", "Deleting the workspace removes every agent, key and log. You can’t undo this.", `<div><button class="btn danger" data-action="modal" data-modal="delete">${I("trash", 16)}Delete workspace</button></div>`);
    if (tab === "keys") body =
      `<div class="alert info" style="margin:4px 0 16px">${I("info", 18)}<div><b>Keep keys secret</b><span class="muted">Anyone with a key can spend from this workspace. Rotate a key right away if it leaks.</span></div></div>` +
      state.keys.map((k, i) => `<div class="key-row"><span class="tile-ic">${I("key", 16)}</span><div style="flex:1;min-width:0"><b style="font-weight:500">${esc(k.name)}</b><div class="faint" style="font-size:12.5px">Created ${k.created} · last used ${k.used}</div></div>
        <span class="key-val hide-mobile">${k.show ? k.key : k.key.slice(0, 8) + "••••••••••" + k.key.slice(-4)}</span>
        <button class="btn ghost sm icon-only" data-action="reveal-key" data-i="${i}" aria-label="${k.show ? "Hide" : "Show"} key">${I("eye", 16)}</button>
        <button class="btn ghost sm icon-only" data-action="copy-key" data-i="${i}" aria-label="Copy key">${I("copy", 16)}</button></div>`).join("") +
      `<div style="margin-top:16px"><button class="btn primary" data-action="modal" data-modal="key">${I("plus", 16)}Create key</button></div>`;
    if (tab === "notifications") body =
      row("Email", "Sent to mara@northwind.io.", toggleRow("Usage alerts", "At 50%, 80% and 100% of quota", true) + toggleRow("Agent failures", "When the error rate goes above 5%", true) + toggleRow("Weekly digest", "Every Monday at 9:00", false)) +
      row("Slack", "Post alerts to a channel.", `<div style="display:flex;gap:8px;flex-wrap:wrap"><input class="input" style="flex:1;min-width:160px" value="#ai-ops" aria-label="Slack channel"><button class="btn">Send test</button></div>`);
    if (tab === "security") body =
      row("Two-factor authentication", "Require a second step at sign-in.", toggleRow("Authenticator app", "Turned on Mar 3, 2026", true) + toggleRow("Require for all members", "Members without 2FA will be asked to set it up", false)) +
      row("Sessions", "Where you’re signed in right now.", [["MacBook Pro · Chrome", "Lisbon · current session"], ["iPhone 16 · Keel app", "Lisbon · 2 hours ago"]].map(([d, w]) => `<div class="list-row"><span class="tile-ic">${I("lock", 16)}</span><div class="grow"><b>${d}</b><small>${w}</small></div><button class="btn sm">Sign out</button></div>`).join("")) +
      row("Audit log", "Every change to agents, keys and members.", `<div><button class="btn" data-action="toast" data-msg="Audit log exported">${I("download", 16)}Export CSV</button></div>`);
    return `${pageHead("Settings", "Workspace preferences, keys and security.")}
      <div class="tabs" role="tablist">${Object.entries(settingsTabs).map(([k, l]) => `<button role="tab" aria-selected="${k === tab}" class="${k === tab ? "on" : ""}" data-action="settings-tab" data-tab="${k}">${l}</button>`).join("")}</div>
      <div class="card card-pad" style="padding-top:4px;padding-bottom:4px">${body}</div>`;
  };

  /* ---------- components (kit page) ---------- */
  screens.components = () => {
    const sw = [["--bg", "Background"], ["--surface", "Surface"], ["--surface-3", "Surface 3"], ["--line", "Line"], ["--text", "Text"], ["--text-2", "Text 2"], ["--accent", "Accent"], ["--signal", "Signal"], ["--warn", "Warn"], ["--danger", "Danger"], ["--c3", "Chart 3"], ["--c4", "Chart 4"]];
    const block = (title, body) => `<div class="card card-pad spec"><h3>${title}</h3>${body}</div>`;
    return `${pageHead("Components", "The building blocks every screen uses. Switch the theme to check both modes.", `<button class="btn" data-action="theme">${I("moon", 16)}Toggle theme</button>`)}
    <div class="grid g-2">
      ${block("Color tokens", `<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(88px,1fr));gap:10px">${sw.map(([v, n]) => `<div class="swatch"><i style="background:var(${v})"></i><span>${n}</span><span class="mono faint" style="font-size:11px">${v}</span></div>`).join("")}</div>`)}
      ${block("Type scale · Geist", `<div class="type-scale">${[["Display 32", 32, 600], ["Title 26", 26, 600], ["Heading 18", 18, 600], ["Body 14", 14, 400], ["Caption 12", 12, 400]].map(([l, s, w]) => `<div><small>${l}</small><span style="font-size:${s}px;font-weight:${w};letter-spacing:${s > 20 ? "-.025em" : "0"}">Steer your AI</span></div>`).join("")}<div><small>Mono 13</small><span class="mono" style="font-size:13px">kl_live_4f9a…e81b</span></div></div>`)}
      ${block("Buttons", `<div class="row-wrap"><button class="btn primary">Primary</button><button class="btn accent">Accent</button><button class="btn">Secondary</button><button class="btn ghost">Ghost</button><button class="btn danger">Danger</button><button class="btn" disabled>Disabled</button></div>
        <div class="row-wrap"><button class="btn sm">Small</button><button class="btn">Default</button><button class="btn lg">Large</button><button class="btn icon-only" aria-label="Add">${I("plus", 16)}</button><button class="btn primary">${I("spark", 16)}With icon</button></div>`)}
      ${block("Inputs", `<div class="field"><label for="c1">Label</label><input id="c1" class="input" placeholder="Placeholder"><span class="hint">Helper text sits under the field.</span></div>
        <div class="field"><label for="c2">With icon</label><div class="input-group">${I("search", 16)}<input id="c2" class="input" placeholder="Search…"></div></div>
        <div class="field"><label for="c3">Error</label><input id="c3" class="input error" value="not-an-email"><span class="hint" style="color:var(--danger)">Enter a valid email address.</span></div>
        <div class="field"><label for="c4">Textarea</label><textarea id="c4" class="textarea" placeholder="System prompt…"></textarea></div>`)}
      ${block("Selection", `<div class="row-wrap"><label class="switch"><input type="checkbox" checked aria-label="On"><span></span></label><label class="switch"><input type="checkbox" aria-label="Off"><span></span></label>
        <label class="check"><input type="checkbox" checked>Checkbox</label><label class="check"><input type="radio" name="r" checked>Radio A</label><label class="check"><input type="radio" name="r">Radio B</label></div>
        ${seg("demo", [["a", "Day"], ["b", "Week"], ["c", "Month"]], "b")}<select class="select"><option>Select menu</option></select><input type="range" class="range" aria-label="Range">`)}
      ${block("Badges, avatars and progress", `<div class="row-wrap"><span class="badge">Neutral</span><span class="badge ok dot">Succeeded</span><span class="badge warn dot">Slow</span><span class="badge err dot">Failed</span><span class="badge info">Beta</span><span class="badge outline">Outline</span></div>
        <div class="row-wrap">${TEAM.slice(0, 4).map((t) => avatar(t.name)).join("")}${avatar("Lena Brandt", "lg")}<div class="avatars">${TEAM.map((t) => avatar(t.name)).join("")}</div></div>
        <div class="bar"><i style="width:64%"></i></div><div class="bar ok"><i style="width:88%"></i></div><div class="bar warn"><i style="width:96%"></i></div>`)}
      ${block("Alerts", `<div class="alert info">${I("info", 18)}<div><b>Info</b><span class="muted">A new model version is available.</span></div></div><div class="alert ok">${I("check", 18)}<div><b>Success</b><span class="muted">Your agent is live.</span></div></div><div class="alert warn">${I("alert", 18)}<div><b>Warning</b><span class="muted">You’ve used 80% of your quota.</span></div></div><div class="alert err">${I("x", 18)}<div><b>Error</b><span class="muted">That key was revoked.</span></div></div>`)}
      ${block("Overlays", `<div class="row-wrap"><button class="btn" data-action="modal" data-modal="invite">Open modal</button><button class="btn" data-action="toast" data-msg="Saved. Changes are live">Show toast</button><button class="btn" data-action="cmdk">${I("command", 16)}Command menu <kbd>⌘K</kbd></button></div>`)}
      ${block("Charts", `${lineChart({ labels: dayLabels(14), h: 180, series: [{ name: "A", values: walk(14, 40, 1, 12, 3), color: "var(--c1)", fill: true }, { name: "B", values: walk(14, 30, 0.5, 10, 8), color: "var(--c3)" }] })}<div class="row-wrap">${[0, 1, 2, 3].map((i) => sparkline(walk(16, 50, 0.6, 8, i + 40), PALETTE[i])).join("")}</div>`)}
      ${block("Empty state", `<div style="text-align:center;padding:20px;display:grid;gap:10px;justify-items:center"><span class="tile-ic" style="width:44px;height:44px">${I("bot", 22)}</span><b>No agents yet</b><span class="muted" style="max-width:280px">Agents run tasks on a trigger, like a new ticket or a nightly schedule.</span><button class="btn primary sm">${I("plus", 14)}Create your first agent</button></div>`)}
    </div>`;
  };
  ICONS.command = '<path d="M9 6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3z"/>';

  /* ---------- full-screen: sign in + onboarding ---------- */
  const authSide = `<div class="auth-side"><span class="orb" style="width:380px;height:380px;background:#4a5bff;top:-80px;right:-60px"></span><span class="orb" style="width:300px;height:300px;background:#b45bd6;top:160px;left:-80px;opacity:.5"></span><span class="orb" style="width:240px;height:240px;background:#13a36b;bottom:120px;right:80px;opacity:.35"></span>
    <blockquote>“We went from guessing what our models cost to knowing, per agent and per customer, in an afternoon.”</blockquote><cite>Head of Platform, a 40-person fintech</cite></div>`;
  screens.signin = () => `<div class="auth"><div class="auth-form"><div>
    <a href="#/overview" class="brand" style="padding:0"><span class="brand-mark">${I("keel", 16)}</span>Keel</a>
    <div><h1>Welcome back</h1><p class="muted" style="margin:6px 0 0">Sign in to your workspace.</p></div>
    <div class="grid g-2" style="gap:10px"><button class="btn" data-action="go" data-route="overview">${I("globe", 16)}Google</button><button class="btn" data-action="go" data-route="overview">${I("code", 16)}GitHub</button></div>
    <div class="divider">or with email</div>
    <form data-form="signin" style="display:grid;gap:14px">
      <div class="field"><label for="em">Work email</label><input id="em" class="input" type="email" placeholder="you@company.com" required></div>
      <div class="field"><label for="pw" style="display:flex;justify-content:space-between">Password <a href="#/signin" class="faint" style="font-weight:400">Forgot?</a></label><input id="pw" class="input" type="password" placeholder="••••••••" required></div>
      <label class="check"><input type="checkbox" checked>Keep me signed in</label>
      <button class="btn primary lg" type="submit">Sign in</button>
    </form>
    <p class="faint" style="margin:0;text-align:center">New to Keel? <a href="#/onboarding" style="color:var(--text)">Create a workspace</a></p>
  </div></div>${authSide}</div>`;

  const ONBOARD = [
    { title: "Name your workspace", sub: "You can change this later.", body: () => `<div class="field"><label for="ob1">Workspace name</label><input id="ob1" class="input" value="Northwind Labs"></div><div class="field"><label for="ob2">Your role</label><select id="ob2" class="select"><option>Engineering</option><option>Product</option><option>Operations</option><option>Founder</option></select></div>` },
    { title: "What will you build first?", sub: "We’ll set up a starter agent for you.", body: () => `<div class="choice-grid">${[["support", "msg", "Support triage", "Tag and answer tickets"], ["research", "search", "Research", "Enrich leads and accounts"], ["docs", "file", "Document AI", "Read invoices and contracts"], ["data", "db", "Data copilot", "Ask questions in plain English"]].map(([k, ic, t, s]) => `<button class="choice ${state.onboardChoice === k ? "on" : ""}" data-action="ob-choice" data-k="${k}"><span class="tile-ic">${I(ic, 16)}</span><span><b>${t}</b><small>${s}</small></span></button>`).join("")}</div>` },
    { title: "Invite your team", sub: "Teammates get access as soon as they accept.", body: () => `<div class="field"><label for="ob3">Emails</label><textarea id="ob3" class="textarea" placeholder="dev@company.com, lena@company.com"></textarea><span class="hint">Separate with commas. You can skip this.</span></div>` }
  ];
  screens.onboarding = () => {
    const s = state.onboardStep, st = ONBOARD[s];
    return `<div class="auth"><div class="auth-form"><div>
      <a href="#/overview" class="brand" style="padding:0"><span class="brand-mark">${I("keel", 16)}</span>Keel</a>
      <div class="steps">${ONBOARD.map((_, i) => `<i class="${i <= s ? "on" : ""}"></i>`).join("")}</div>
      <div><span class="faint" style="font-size:12.5px">Step ${s + 1} of ${ONBOARD.length}</span><h1 style="margin-top:4px">${st.title}</h1><p class="muted" style="margin:6px 0 0">${st.sub}</p></div>
      ${st.body()}
      <div style="display:flex;gap:8px;justify-content:space-between"><button class="btn ghost" data-action="ob-back" ${s === 0 ? "disabled" : ""}>Back</button><button class="btn primary" data-action="ob-next">${s === ONBOARD.length - 1 ? "Finish setup" : "Continue"}</button></div>
    </div></div>${authSide}</div>`;
  };

  /* ================= shell ================= */
  const NAV = [
    ["Main", [["overview", "Overview", "home"], ["assistant", "Assistant", "spark"], ["agents", "Agents", "bot", "6"], ["usage", "Usage", "chart"], ["billing", "Billing", "card"]]],
    ["Workspace", [["team", "Team", "users"], ["settings", "Settings", "gear"]]],
    ["UI kit", [["components", "Components", "layers"], ["signin", "Sign in", "lock"], ["onboarding", "Onboarding", "star"]]]
  ];
  const TITLES = Object.fromEntries(NAV.flatMap(([, items]) => items.map(([k, l]) => [k, l])));
  const FULLSCREEN = new Set(["signin", "onboarding"]);
  const route = () => {
    const r = (location.hash.replace(/^#\/?/, "") || "overview").split("?")[0];
    return screens[r] ? r : "overview";
  };
  const isDark = () => {
    const t = document.documentElement.dataset.theme;
    return t ? t === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  };
  let collapsed = false;
  try { collapsed = localStorage.getItem("keel-collapsed") === "1"; } catch (e) {}

  function shell(r, inner) {
    return `<div class="app ${collapsed ? "collapsed" : ""}" id="app">
      <aside class="sidebar" aria-label="Main navigation">
        <a href="#/overview" class="brand"><span class="brand-mark">${I("keel", 16)}</span><span class="hide-collapsed">Keel</span></a>
        <button class="workspace" data-action="toast" data-msg="Workspace switcher would open here"><span class="ws-avatar"></span><span class="hide-collapsed" style="min-width:0;flex:1">Northwind Labs<small>Team plan · 6 seats</small></span><span class="hide-collapsed faint">${I("chev", 16)}</span></button>
        ${NAV.map(([label, items]) => `<div class="nav-label hide-collapsed">${label}</div><nav class="nav">${items.map(([k, l, ic, c]) => `<a href="#/${k}" class="${k === r ? "active" : ""}" title="${l}" ${k === r ? 'aria-current="page"' : ""}>${I(ic, 18)}<span class="hide-collapsed">${l}</span>${c ? `<span class="count hide-collapsed">${c}</span>` : ""}</a>`).join("")}</nav>`).join("")}
        <div class="sidebar-foot">
          <div class="credits hide-collapsed"><div class="row"><span class="muted">Tokens this month</span><b class="num">78%</b></div><div class="bar warn"><i style="width:78%"></i></div><button class="btn sm" style="width:100%;margin-top:12px" data-action="go" data-route="billing">Upgrade plan</button></div>
        </div>
      </aside>
      <div class="scrim" data-action="close-nav"></div>
      <div class="main">
        <header class="topbar">
          <button class="btn ghost sm icon-only only-mobile" data-action="open-nav" aria-label="Open menu">${I("menu", 18)}</button>
          <button class="btn ghost sm icon-only hide-mobile" data-action="collapse" aria-label="Collapse sidebar">${I("panel", 18)}</button>
          <div class="crumbs"><span class="hide-mobile">Northwind Labs</span><span class="hide-mobile">/</span><b>${TITLES[r]}</b></div>
          <button class="search" data-action="cmdk" aria-label="Search or jump to">${I("search", 16)}<span>Search or jump to…</span><kbd>⌘K</kbd></button>
          <button class="btn ghost sm icon-only" data-action="theme" aria-label="Toggle theme">${I(isDark() ? "sun" : "moon", 18)}</button>
          <div style="position:relative"><button class="btn ghost sm icon-only" data-action="menu" data-menu="notif" aria-label="Notifications">${I("bell", 18)}</button><span style="position:absolute;top:5px;right:6px;width:7px;height:7px;border-radius:50%;background:var(--danger);border:2px solid var(--bg)"></span></div>
          <button data-action="menu" data-menu="profile" style="border:0;background:none;padding:0;cursor:pointer" aria-label="Account menu">${avatar("Mara Okafor")}</button>
        </header>
        <main class="content" id="content">${inner}</main>
      </div>
    </div>`;
  }

  function render() {
    const r = route();
    const root = $("#root");
    closeMenu();
    if (FULLSCREEN.has(r)) root.innerHTML = screens[r]();
    else root.innerHTML = shell(r, screens[r]());
    document.title = (TITLES[r] || "Keel") + " · Keel";
    if (r === "assistant") {
      const box = $("#messages"); if (box) box.scrollTop = box.scrollHeight;
    }
  }

  /* ================= overlays ================= */
  function toast(msg) {
    const el = document.createElement("div");
    el.className = "toast";
    el.innerHTML = `${I("check", 16)}<span>${esc(msg)}</span>`;
    $("#toasts").appendChild(el);
    setTimeout(() => { el.style.transition = "opacity .2s"; el.style.opacity = "0"; setTimeout(() => el.remove(), 220); }, 2600);
  }

  let menuEl = null;
  function closeMenu() { if (menuEl) { menuEl.remove(); menuEl = null; } }
  function openMenu(btn, kind) {
    if (menuEl && menuEl.dataset.kind === kind) return closeMenu();
    closeMenu();
    const m = document.createElement("div");
    m.className = "menu";
    m.dataset.kind = kind;
    if (kind === "profile") m.innerHTML = `<div style="padding:8px 10px"><b>Mara Okafor</b><div class="faint" style="font-size:12.5px">mara@northwind.io</div></div><hr>
      <button data-action="go" data-route="settings">${I("gear", 16)}Settings</button><button data-action="go" data-route="billing">${I("card", 16)}Billing</button><button data-action="theme">${I(isDark() ? "sun" : "moon", 16)}${isDark() ? "Light" : "Dark"} mode</button><hr>
      <button data-action="go" data-route="signin">${I("logout", 16)}Sign out</button>`;
    else m.innerHTML = `<div style="padding:8px 10px;display:flex;justify-content:space-between"><b>Notifications</b><span class="faint" style="font-size:12.5px">3 new</span></div><hr>
      ${[["alert", "Invoice Reader failed 14 times", "21 min ago"], ["users", "Dev Raman invited Aiko Sato", "2 h ago"], ["zap", "You’ve used 78% of your tokens", "Today"]].map(([ic, t, w]) => `<button data-action="close-menu" style="align-items:flex-start">${I(ic, 16)}<span>${t}<small class="faint" style="display:block">${w}</small></span></button>`).join("")}`;
    m.style.width = kind === "notif" ? "300px" : "230px";
    document.body.appendChild(m);
    const r = btn.getBoundingClientRect();
    m.style.position = "fixed";
    m.style.top = r.bottom + 8 + "px";
    m.style.left = Math.max(12, Math.min(innerWidth - m.offsetWidth - 12, r.right - m.offsetWidth)) + "px";
    menuEl = m;
  }

  function modal(html, center = true) {
    const o = document.createElement("div");
    o.className = "overlay" + (center ? " center" : "");
    o.innerHTML = html;
    o.addEventListener("mousedown", (e) => { if (e.target === o) closeModal(o); });
    document.body.appendChild(o);
    requestAnimationFrame(() => o.classList.add("open"));
    const f = o.querySelector("input, textarea, select, button.primary");
    if (f) f.focus();
    return o;
  }
  function closeModal(o = $(".overlay.open")) {
    if (!o) return;
    o.classList.remove("open");
    setTimeout(() => o.remove(), 160);
  }
  const MODALS = {
    invite: () => `<div class="dialog" role="dialog" aria-modal="true" aria-labelledby="mi"><div class="dialog-head"><h3 id="mi">Invite people</h3><p>They’ll get an email with a link to join Northwind Labs.</p></div>
      <div class="dialog-body"><div class="field"><label for="iv">Email addresses</label><input id="iv" class="input" placeholder="name@company.com, …"></div>
      <div class="field"><label for="ir">Role</label><select id="ir" class="select"><option>Developer</option><option>Analyst</option><option>Viewer</option><option>Admin</option></select><span class="hint">Developers can create agents and keys. Analysts can only read.</span></div></div>
      <div class="dialog-foot"><button class="btn" data-action="close-modal">Cancel</button><button class="btn primary" data-action="close-modal" data-msg="Invites sent">Send invites</button></div></div>`,
    key: () => `<div class="dialog" role="dialog" aria-modal="true" aria-labelledby="mk"><div class="dialog-head"><h3 id="mk">Create API key</h3><p>You’ll only see the full key once, so copy it somewhere safe.</p></div>
      <div class="dialog-body"><div class="field"><label for="kn">Name</label><input id="kn" class="input" placeholder="e.g. Mobile app"></div>
      <div class="field"><label>Permissions</label><div class="seg"><button class="on" data-action="seg-local">Full access</button><button data-action="seg-local">Read only</button></div></div>
      <div class="field"><label for="kb">Monthly budget (USD)</label><input id="kb" class="input" type="number" value="250"></div></div>
      <div class="dialog-foot"><button class="btn" data-action="close-modal">Cancel</button><button class="btn primary" data-action="create-key">Create key</button></div></div>`,
    agent: () => `<div class="dialog" role="dialog" aria-modal="true" aria-labelledby="ma"><div class="dialog-head"><h3 id="ma">New agent</h3><p>Describe the job. Keel drafts the steps and you review them before it goes live.</p></div>
      <div class="dialog-body"><div class="field"><label for="an">Name</label><input id="an" class="input" placeholder="e.g. Refund helper"></div>
      <div class="field"><label for="ad">What should it do?</label><textarea id="ad" class="textarea" placeholder="When a refund request comes in, check the order and draft a reply…"></textarea></div>
      <div class="grid g-2" style="gap:12px"><div class="field"><label for="am">Model</label><select id="am" class="select">${MODELS.slice(0, 3).map((m) => `<option>${m.name}</option>`).join("")}</select></div><div class="field"><label for="at">Trigger</label><select id="at" class="select"><option>New ticket</option><option>Webhook</option><option>Schedule</option><option>Manual</option></select></div></div></div>
      <div class="dialog-foot"><button class="btn" data-action="close-modal">Cancel</button><button class="btn primary" data-action="close-modal" data-msg="Draft agent created. Review its steps before going live">${I("spark", 16)}Draft agent</button></div></div>`,
    delete: () => `<div class="dialog" role="alertdialog" aria-modal="true" aria-labelledby="md" style="max-width:440px"><div class="dialog-head"><h3 id="md">Delete Northwind Labs?</h3><p>This permanently removes 6 agents, 3 API keys and 90 days of logs.</p></div>
      <div class="dialog-body"><div class="field"><label for="dc">Type <b class="mono">northwind</b> to confirm</label><input id="dc" class="input" data-confirm="northwind" autocomplete="off"></div></div>
      <div class="dialog-foot"><button class="btn" data-action="close-modal">Cancel</button><button class="btn" style="background:var(--danger);border-color:var(--danger);color:#fff" disabled id="del-btn" data-action="close-modal" data-msg="Demo only, nothing was deleted">Delete workspace</button></div></div>`
  };

  /* command palette */
  function commands() {
    const nav = NAV.flatMap(([, items]) => items.map(([k, l, ic]) => ({ group: "Go to", label: l, icon: ic, run: () => (location.hash = "#/" + k) })));
    return [
      ...nav,
      { group: "Actions", label: "Ask Keel a question", icon: "spark", run: () => { state.activeThread = null; location.hash = "#/assistant"; render(); } },
      { group: "Actions", label: "Toggle light / dark theme", icon: "moon", hint: "⇧D", run: toggleTheme },
      { group: "Actions", label: "Invite people", icon: "users", run: () => modal(MODALS.invite()) },
      { group: "Actions", label: "Create API key", icon: "key", run: () => modal(MODALS.key()) },
      { group: "Actions", label: "New agent", icon: "bot", run: () => modal(MODALS.agent()) }
    ];
  }
  function openCmdk() {
    if ($(".overlay.cmdk")) return;
    const o = modal(`<div class="dialog" role="dialog" aria-modal="true" aria-label="Command menu"><div class="cmdk-input">${I("search", 18, "faint")}<input placeholder="Type a command or search…" aria-label="Command"><kbd>Esc</kbd></div><div class="cmdk-list"></div></div>`, false);
    o.classList.add("cmdk");
    const input = $("input", o), list = $(".cmdk-list", o);
    let sel = 0, items = [];
    const draw = () => {
      const q = input.value.toLowerCase().trim();
      items = commands().filter((c) => !q || c.label.toLowerCase().includes(q));
      sel = Math.min(sel, Math.max(0, items.length - 1));
      if (!items.length) { list.innerHTML = `<div class="cmdk-empty">No results for “${esc(input.value)}”. Press Enter to ask Keel instead.</div>`; return; }
      let g = "", html = "";
      items.forEach((c, i) => {
        if (c.group !== g) { g = c.group; html += `<div class="cmdk-group">${g}</div>`; }
        html += `<button class="cmdk-item ${i === sel ? "sel" : ""}" data-i="${i}">${I(c.icon, 16)}<span>${c.label}</span>${c.hint ? `<kbd>${c.hint}</kbd>` : ""}</button>`;
      });
      list.innerHTML = html;
      const s = $(".cmdk-item.sel", list); if (s) s.scrollIntoView({ block: "nearest" });
    };
    const runSel = (i) => {
      const q = input.value.trim();
      closeModal(o);
      if (items[i]) items[i].run();
      else if (q) { state.activeThread = null; ask(q); }
    };
    input.addEventListener("input", () => { sel = 0; draw(); });
    input.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") { sel = Math.min(items.length - 1, sel + 1); draw(); e.preventDefault(); }
      if (e.key === "ArrowUp") { sel = Math.max(0, sel - 1); draw(); e.preventDefault(); }
      if (e.key === "Enter") { runSel(sel); e.preventDefault(); }
    });
    list.addEventListener("click", (e) => { const b = e.target.closest(".cmdk-item"); if (b) runSel(+b.dataset.i); });
    list.addEventListener("mousemove", (e) => { const b = e.target.closest(".cmdk-item"); if (b && +b.dataset.i !== sel) { sel = +b.dataset.i; draw(); } });
    draw();
  }

  function toggleTheme() {
    const next = isDark() ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("keel-theme", next); } catch (e) {}
    render();
  }

  /* ================= events ================= */
  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-action]");
    if (menuEl && !e.target.closest(".menu") && !(t && t.dataset.action === "menu")) closeMenu();
    if (!t) return;
    const a = t.dataset.action, d = t.dataset;
    switch (a) {
      case "go":
        closeMenu();
        if (location.hash === "#/" + d.route) render(); else location.hash = "#/" + d.route;
        if (d.scroll) setTimeout(() => { const el = document.getElementById(d.scroll); if (el) el.scrollIntoView({ behavior: "smooth" }); }, 50);
        break;
      case "toast": toast(d.msg); break;
      case "theme": closeMenu(); toggleTheme(); break;
      case "collapse":
        collapsed = !collapsed;
        try { localStorage.setItem("keel-collapsed", collapsed ? "1" : "0"); } catch (err) {}
        $("#app").classList.toggle("collapsed", collapsed);
        break;
      case "open-nav": $("#app").classList.add("nav-open"); break;
      case "close-nav": $("#app").classList.remove("nav-open"); break;
      case "cmdk": openCmdk(); break;
      case "menu": openMenu(t, d.menu); break;
      case "close-menu": closeMenu(); break;
      case "seg":
        if (d.name === "yearly") state.yearly = d.value === "1";
        else if (d.name in state) state[d.name] = +d.value;
        else { $$("button", t.parentElement).forEach((b) => b.classList.toggle("on", b === t)); break; }
        render();
        break;
      case "seg-local": $$("button", t.parentElement).forEach((b) => b.classList.toggle("on", b === t)); break;
      case "ask": state.activeThread = null; ask(d.prompt); break;
      case "new-chat": state.activeThread = null; render(); setTimeout(() => $("#prompt") && $("#prompt").focus(), 0); break;
      case "thread": state.activeThread = d.id; render(); break;
      case "copy-msg": {
        const text = t.closest(".bubble").innerText.trim();
        navigator.clipboard?.writeText(text).catch(() => {});
        toast("Copied to clipboard");
        break;
      }
      case "run-flow": runFlow(); break;
      case "settings-tab": state.settingsTab = d.tab; render(); break;
      case "reveal-key": state.keys[+d.i].show = !state.keys[+d.i].show; render(); break;
      case "copy-key": navigator.clipboard?.writeText(state.keys[+d.i].key).catch(() => {}); toast(`Copied “${state.keys[+d.i].name}” key`); break;
      case "modal": modal(MODALS[d.modal]()); break;
      case "close-modal": closeModal(t.closest(".overlay")); if (d.msg) toast(d.msg); break;
      case "create-key": {
        const o = t.closest(".overlay");
        const name = ($("#kn", o).value || "Untitled key").trim();
        const hex = Array.from({ length: 18 }, () => "0123456789abcdef"[Math.floor(Math.random() * 16)]).join("");
        state.keys.unshift({ name, key: "kl_live_" + hex, created: "Oct 31, 2026", used: "Never", show: true });
        closeModal(o);
        state.settingsTab = "keys";
        if (route() === "settings") render(); else location.hash = "#/settings";
        toast(`Key “${name}” created. Copy it now`);
        break;
      }
      case "ob-next":
        if (state.onboardStep < ONBOARD.length - 1) { state.onboardStep++; render(); }
        else { state.onboardStep = 0; location.hash = "#/overview"; setTimeout(() => toast("Workspace ready. Your starter agent is drafting"), 100); }
        break;
      case "ob-back": state.onboardStep = Math.max(0, state.onboardStep - 1); render(); break;
      case "ob-choice": state.onboardChoice = d.k; render(); break;
    }
  });
  document.addEventListener("change", (e) => {
    const t = e.target;
    if (t.dataset.action === "toggle-agent") {
      const ag = state.agents.find((x) => x.id === t.dataset.id);
      ag.on = t.checked;
      toast(`${ag.name} ${ag.on ? "is live" : "paused"}`);
      render();
    }
    if (t.dataset.action === "role") toast(`${t.dataset.name} is now ${t.value === "Admin" ? "an" : "a"} ${t.value}`);
    if (t.dataset.action === "toast-toggle") toast(`${t.dataset.label} ${t.checked ? "on" : "off"}`);
  });
  document.addEventListener("input", (e) => {
    const t = e.target;
    if (t.dataset.action === "temp") $("#temp-val").textContent = (+t.value).toFixed(1);
    if (t.dataset.filter === "team") {
      const q = t.value.toLowerCase();
      $$("#team-body tr").forEach((tr) => (tr.style.display = tr.dataset.name.includes(q) ? "" : "none"));
    }
    if (t.dataset.confirm) $("#del-btn").disabled = t.value !== t.dataset.confirm;
    if (t.id === "prompt") { t.style.height = "auto"; t.style.height = Math.min(200, t.scrollHeight) + "px"; }
  });
  document.addEventListener("submit", (e) => {
    const f = e.target.dataset.form;
    if (!f) return;
    e.preventDefault();
    if (f === "chat") { const ta = $("#prompt"); const q = ta.value; ta.value = ""; ask(q); }
    if (f === "signin") { location.hash = "#/overview"; setTimeout(() => toast("Signed in as Mara Okafor"), 100); }
  });
  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openCmdk(); return; }
    if (e.key === "Escape") { closeMenu(); closeModal(); const app = $("#app"); if (app) app.classList.remove("nav-open"); }
    if (e.target.id === "prompt" && e.key === "Enter" && !e.shiftKey && !e.isComposing) {
      e.preventDefault();
      e.target.form.requestSubmit();
    }
    const typing = /INPUT|TEXTAREA|SELECT/.test(e.target.tagName);
    if (!typing && e.shiftKey && e.key.toLowerCase() === "d") toggleTheme();
  });

  /* chart tooltips */
  const tip = $("#tip");
  document.addEventListener("mousemove", (e) => {
    const t = e.target.closest && e.target.closest("[data-tip]");
    if (!t) { tip.classList.remove("show"); return; }
    const [head, ...lines] = t.dataset.tip.split("|");
    tip.innerHTML = `<div style="opacity:.7;margin-bottom:3px">${esc(head)}</div>${lines.map((l) => { const [k, v] = l.split(": "); return `<div style="display:flex;justify-content:space-between;gap:14px"><span>${esc(k)}</span><b>${esc(v ?? "")}</b></div>`; }).join("")}`;
    tip.classList.add("show");
    const w = tip.offsetWidth, h = tip.offsetHeight;
    let x = e.clientX + 14, y = e.clientY - h - 12;
    if (x + w > innerWidth - 8) x = e.clientX - w - 14;
    if (y < 8) y = e.clientY + 16;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  });

  window.addEventListener("hashchange", () => { window.scrollTo(0, 0); render(); });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { if (!document.documentElement.dataset.theme) render(); });
  render();
})();
