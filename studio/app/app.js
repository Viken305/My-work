// BrighterMinds Video Studio: the dashboard (plain JS, no build step). Talks to studio/server.py.
"use strict";

const S = {
  route: [], projects: [], pid: null, p: null, insp: null, jobs: [], git: {}, files: null, art: [],
  saveState: "saved", sel: { part: null, line: null, shot: null, t: 0, editing: null },
  quality: localStorage.getItem("quality") || "final", preview: [], safe: true, collapsed: {}, pendingRender: false,
};
const $ = (q) => document.querySelector(q);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (t) => (t == null || isNaN(t) ? "—" : `${Math.floor(t / 60)}:${(t % 60).toFixed(1).padStart(4, "0")}`);
const clean = (w) => w.toLowerCase().replace(/[^\w']/g, "");
const PART_COLORS = ["#ffb547", "#ffc977", "#b6a4ff", "#8b6cff", "#d9d4ff", "#ffd9a0", "#a08cff", "#ffe2b8"];

async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts,
    body: opts.body && typeof opts.body !== "string" ? JSON.stringify(opts.body) : opts.body });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
}

function toast(msg, bad = false) {
  const el = document.createElement("div");
  el.className = "toast" + (bad ? " bad" : "");
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), bad ? 6000 : 3000);
}

// ---------------------------------------------------------------- paths into the project object
function getp(path, o = S.p) { return path.split(".").reduce((x, k) => (x == null ? x : x[k]), o); }
function setp(path, v, o = S.p) {
  const ks = path.split(".");
  let x = o;
  ks.slice(0, -1).forEach((k) => { if (x[k] == null) x[k] = {}; x = x[k]; });
  x[ks.at(-1)] = v;
}

// ---------------------------------------------------------------- saving
let saveTimer = null, inspTimer = null;
function changed(reRender = false) {
  S.saveState = "dirty";
  updateSaved();
  clearTimeout(saveTimer);
  saveTimer = setTimeout(save, 700);
  if (reRender) render();
}
async function save() {
  if (!S.p) return;
  S.saveState = "saving"; updateSaved();
  try {
    await api(`/api/p/${S.pid}`, { method: "PUT", body: S.p });
    S.saveState = "saved";
    clearTimeout(inspTimer);
    inspTimer = setTimeout(() => loadInspect(true), 400);
  } catch (e) { S.saveState = "error"; toast("Could not save: " + e.message, true); }
  updateSaved();
}
function updateSaved() {
  const el = $("#saved");
  if (!el) return;
  el.className = "saved" + (S.saveState === "saved" ? "" : " dirty");
  el.textContent = { saved: "All changes saved ✓", dirty: "Unsaved…", saving: "Saving…", error: "Save failed" }[S.saveState];
}

// ---------------------------------------------------------------- data
async function loadProject(pid) {
  if (S.pid !== pid) {
    S.pid = pid; S.p = null; S.insp = null; S.files = null; S.art = [];
    S.sel = { part: null, line: null, shot: null, t: 0, editing: null };
  }
  S.p = await api(`/api/p/${pid}`);
  render();
  loadInspect();
  loadFiles();
}
async function loadInspect(fresh = false) {
  if (!S.pid) return;
  try { S.insp = await api(`/api/p/${S.pid}/inspect${fresh ? "?fresh=1" : ""}`); } catch (e) { S.insp = { error: e.message, parts: [] }; }
  safeRender();
}
async function loadFiles() {
  if (!S.pid) return;
  try {
    S.files = await api(`/api/p/${S.pid}/files`);
    S.art = (await api(`/api/p/${S.pid}/files?dir=out/art`)).files || [];
  } catch (e) { S.files = { files: [] }; }
  safeRender();
}
async function poll() {
  try {
    const before = S.jobs.filter((j) => j.status === "running" || j.status === "queued").map((j) => j.id);
    S.jobs = await api("/api/jobs");
    const finished = S.jobs.filter((j) => before.includes(j.id) && !["running", "queued"].includes(j.status));
    for (const j of finished) onJobDone(j);
    if (S.jobs.some((j) => j.status === "running") || finished.length) safeRender(true);
  } catch (e) { /* server restarting */ }
  const busy = S.jobs.some((j) => j.status === "running" || j.status === "queued");
  setTimeout(poll, busy ? 1200 : 4000);
}
function onJobDone(j) {
  if (j.status === "done") toast(`✓ ${j.label}`); else if (j.status === "failed") toast(`✗ ${j.label} failed. See the log on the Render page.`, true);
  if (j.status !== "done") return;
  if (j.spec.kind === "still" && j.result) {
    const url = `/f/${j.project}/${j.result.split(`/${j.project}/`).pop()}?v=${Date.now()}`;
    S.preview.unshift({ url, label: `${j.spec.part} @ ${j.spec.times[0]}s`, t: j.spec.t_abs });
    S.preview = S.preview.slice(0, 6);
    S.stillShown = S.route[2] === "scenes" ? url : S.stillShown;
  }
  if (j.spec.kind === "preview" && j.result) playAudio(`/f/${j.project}/${j.result.split(`/${j.project}/`).pop()}`);
  if (j.spec.kind === "audio") playAudio(`/f/${j.project}/build/${j.spec.part}/mix.wav?v=${Date.now()}`);
  loadInspect(true);
  loadFiles();
  refreshProjects();
}
async function refreshProjects() { try { S.projects = await api("/api/projects"); safeRender(); } catch (e) { /* ignore */ } }
async function refreshGit() { try { S.git = await api("/api/git"); } catch (e) { S.git = {}; } safeRender(); }

async function job(spec) {
  try {
    if (S.saveState !== "saved") { clearTimeout(saveTimer); await save(); }
    const j = await api(`/api/p/${S.pid}/jobs`, { method: "POST", body: spec });
    S.jobs.unshift(j);
    toast(`Started: ${j.label}`);
    render();
  } catch (e) { toast(e.message, true); }
}

let audioEl = null;
function playAudio(url) {
  if (audioEl) audioEl.pause();
  audioEl = new Audio(url + (url.includes("?") ? "" : `?v=${Date.now()}`));
  audioEl.play().catch(() => toast("Could not play audio", true));
}

// ---------------------------------------------------------------- rendering
function safeRender(soft = false) {
  const a = document.activeElement;
  if (a && ["INPUT", "TEXTAREA", "SELECT"].includes(a.tagName) && a.closest("main")) {
    S.pendingRender = true;
    if (soft) updateJobsBox();
    return;
  }
  render();
}
document.addEventListener("focusout", () => setTimeout(() => {
  const a = document.activeElement;
  if (S.pendingRender && !(a && ["INPUT", "TEXTAREA", "SELECT"].includes(a.tagName))) { S.pendingRender = false; render(); }
}, 50));

function render() {
  const keep = $("main")?.scrollTop;
  const video = $("#player");
  const vt = video ? video.currentTime : null;
  const playing = video && !video.paused;
  const view = S.route[0] === "p" && S.p ? ({ script: viewScript, scenes: viewScenes, style: viewStyle, render: viewRender }[S.route[2]] || viewScript)() : viewProjects();
  $("#app").innerHTML = nav() + `<main>${view}</main>`;
  if (keep) $("main").scrollTop = keep;
  const v2 = $("#player");
  if (v2 && vt != null) { v2.currentTime = vt; if (playing) v2.play(); }
  wire();
}

function nav() {
  const pid = S.pid, on = S.route[0] === "p" ? S.route[2] || "script" : "projects";
  const item = (id, n, name, href) =>
    `<a class="${id === on ? "on" : ""} ${href ? "" : "off"}" href="${href || "#"}"><i>${n}</i>${name}</a>`;
  const running = S.jobs.filter((j) => j.status === "running" || j.status === "queued");
  const git = S.git || {};
  return `<nav>
    <div class="brand"><div class="logo"></div><div><b>BrighterMinds</b><span>VIDEO STUDIO</span></div></div>
    ${S.route[0] === "p" && S.p ? `<div class="proj"><small>PROJECT</small><div>${esc(S.p.title)}</div></div>` : ""}
    ${item("projects", "⌂", "Projects", "#/")}
    ${item("script", "1", "Script &amp; Voice", pid && S.route[0] === "p" ? `#/p/${pid}/script` : null)}
    ${item("scenes", "2", "Scenes &amp; Timeline", pid && S.route[0] === "p" ? `#/p/${pid}/scenes` : null)}
    ${item("style", "3", "Style &amp; Sound", pid && S.route[0] === "p" ? `#/p/${pid}/style` : null)}
    ${item("render", "4", "Render &amp; Publish", pid && S.route[0] === "p" ? `#/p/${pid}/render` : null)}
    <div class="grow"></div>
    <div id="jobsbox">${jobsBox(running)}</div>
    <div class="git">${git.error ? esc(git.error) : `GitHub · ${esc(git.repo || "")}<br>branch <b>${esc((git.branch || "").replace(/^claude\//, "…/"))}</b><br>${git.changed ? (git.changed.length ? `${git.changed.length} unsaved file(s)` : "everything saved ✓") : ""}`}</div>
  </nav>`;
}
function jobsBox(running) {
  if (!running.length) return "";
  const j = running.find((x) => x.status === "running") || running[0];
  const pr = j.progress;
  return `<div class="jobsbox"><b>${esc(j.label)}</b>${running.length > 1 ? ` · +${running.length - 1} queued` : ""}<br>
    ${pr ? `${pr.part}: ${pr.done}/${pr.total} frames` : esc(j.status)}
    <div class="pbar"><i style="width:${pr ? (100 * pr.done / pr.total).toFixed(1) : j.status === "running" ? 15 : 0}%"></i></div></div>`;
}
function updateJobsBox() {
  const el = $("#jobsbox");
  if (el) el.innerHTML = jobsBox(S.jobs.filter((j) => j.status === "running" || j.status === "queued"));
}

function header(step, title, right = "") {
  return `<header><div><div class="step">${step}</div><h1>${title}</h1></div><div class="sp"></div>
    ${S.p ? `<span id="saved" class="saved"></span>` : ""}${right}</header>`;
}

// ---------------------------------------------------------------- helpers over the inspect data
function partInfo(id) { return (S.insp?.parts || []).find((x) => x.id === id); }
function lineInfo(lid) {
  for (const pt of S.insp?.parts || []) for (const ln of pt.lines || []) if (ln.id === lid) return { part: pt, line: ln };
  return null;
}
function estSeconds(text) { return text.trim().split(/\s+/).filter(Boolean).length / 2.55; }
function partSeconds(part) {
  const info = partInfo(part.id);
  if (info?.ready) return info.duration;
  const L = info?.lengths || {};
  return 0.4 + part.lines.reduce((a, l) => a + (L[l.id] && !(info.stale_voice || []).includes(l.id) ? L[l.id] : estSeconds(l.text)) + (S.p.voice.gap ?? 0.5), 0) + 0.6;
}
function totalSeconds() { return S.p.parts.reduce((a, p) => a + partSeconds(p), 0); }
function anchoredLines() {
  const out = {};
  for (const pt of S.insp?.parts || []) Object.entries(pt.anchors || {}).forEach(([k, ws]) => (out[k] = ws));
  return out;
}
function missingAnchors() { return (S.insp?.parts || []).flatMap((p) => (p.missing_anchors || []).map((m) => ({ part: p.id, line: m[0], word: m[1] }))); }
function staleVoice() { return (S.insp?.parts || []).flatMap((p) => (p.stale_voice || []).map((l) => ({ part: p.id, line: l }))); }

// ---------------------------------------------------------------- projects
function viewProjects() {
  const ed = S.projects.filter((p) => p.editable), code = S.projects.filter((p) => !p.editable);
  const ready = ed.filter((p) => p.stages?.render === "done" && !p.posted);
  const voices = S.insp?.voices || ["af_heart"];
  const card = (p) => {
    const st = p.stages || {};
    const chip = p.posted ? `<span class="chip g"><span class="dot"></span>POSTED</span>`
      : st.render === "done" ? `<span class="chip g"><span class="dot"></span>READY TO POST</span>`
      : st.voice !== "done" ? `<span class="chip a"><span class="dot"></span>SCRIPT · VOICE</span>`
      : `<span class="chip v"><span class="dot"></span>IN PROGRESS</span>`;
    return `<div class="vid" data-go="#/p/${p.id}/script"><div class="cover" style="${p.thumb ? `background-image:url(${p.thumb})` : ""}">
      <span class="chip a fmt">${esc(p.format)}</span><span class="len">${p.total ? fmt(p.total).replace(/\.\d$/, "") : "—"}</span></div>
      <div class="meta"><b>${esc(p.title)}</b>${chip}
      <div class="pipe">${["script", "voice", "scenes", "render", "post"].map((k) => `<i class="${st[k] || ""}" title="${k}: ${st[k] || "todo"}"></i>`).join("")}</div></div></div>`;
  };
  const nv = S.newVideo || (S.newVideo = { topic: "", format: "9:16", target: 100, parts: 5, voice: "af_heart" });
  return header("HOME", "Your videos") + `
  <div class="stats" style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px">
    <div class="panel"><h3>Studio videos</h3><div style="font-size:26px;font-weight:800">${ed.length}</div><span class="muted">${code.length} older videos (code only)</span></div>
    <div class="panel"><h3>Ready to post</h3><div style="font-size:26px;font-weight:800" class="green">${ready.length}</div><span class="muted">${esc(ready.map((p) => p.title).join(", ") || "none yet")}</span></div>
    <div class="panel"><h3>Jobs running</h3><div style="font-size:26px;font-weight:800">${S.jobs.filter((j) => j.status === "running").length}</div><span class="muted">${S.jobs.filter((j) => j.status === "queued").length} queued</span></div>
    <div class="panel"><h3>Shorts limit</h3><div style="font-size:26px;font-weight:800">3:00</div><span class="muted">keep every video under it</span></div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 400px;gap:18px;align-items:start">
    <div>
      <div class="pgrid">${ed.map(card).join("")}</div>
      ${code.length ? `<h3 class="muted" style="font:700 11px Mono;letter-spacing:.18em;margin:22px 0 10px">OLDER VIDEOS · MADE BEFORE THE STUDIO (CODE ONLY)</h3>
      <div class="pgrid">${code.map((p) => `<div class="vid code"><div class="cover" style="background:linear-gradient(135deg,#1d1c25,#2a2735)"></div><div class="meta"><b>${esc(p.title)}</b><span class="muted">${esc(p.id)}/</span></div></div>`).join("")}</div>` : ""}
    </div>
    <div class="panel">
      <h3>New video</h3>
      <div class="field"><label>Topic</label><input data-nv="topic" value="${esc(nv.topic)}" placeholder="How do noise-cancelling headphones work?"></div>
      <div class="field"><label>Format</label><div class="seg">${["9:16", "16:9"].map((f) => `<div class="${nv.format === f ? "on" : ""}" data-nvset="format" data-v="${f}">${f === "9:16" ? "Short 9:16" : "Wide 16:9"}</div>`).join("")}</div></div>
      <div class="field"><label>Target length <b id="nvt">${fmt(nv.target).replace(/\.\d$/, "")}</b></label><input type="range" min="30" max="180" step="5" value="${nv.target}" data-nv="target" data-out="nvt"></div>
      <div class="field"><label>Parts <b id="nvp">${nv.parts}</b></label><input type="range" min="1" max="8" value="${nv.parts}" data-nv="parts" data-out="nvp"></div>
      <div class="field"><label>Voice</label><select data-nv="voice">${voices.map((v) => `<option ${v === nv.voice ? "selected" : ""}>${v}</option>`).join("")}</select></div>
      <div class="muted" style="margin-bottom:12px">Creates a new folder with the same engine, style and voice settings as your last video. You can write and voice the script right away. Animation for a brand-new topic is code: ask Claude to animate it.</div>
      <span class="btn primary" data-act="newVideo" style="justify-content:center;display:flex">＋ Create video</span>
    </div>
  </div>`;
}

// ---------------------------------------------------------------- script & voice
function lineHtml(part, ln, anchors, stale) {
  const li = lineInfo(ln.id);
  const words = S.p.words.map(clean), model = S.p.model.map(clean);
  const anc = (anchors[ln.id] || []).map(clean);
  const lost = missingAnchors().filter((m) => m.line === ln.id).map((m) => clean(m.word));
  const toks = ln.text.split(/\s+/).filter(Boolean);
  const say = new Set();
  for (const [spoken] of S.p.display) {
    const sw = spoken.toLowerCase().split(/\s+/);
    for (let i = 0; i + sw.length <= toks.length; i++)
      if (sw.every((w, j) => clean(toks[i + j]) === w)) for (let j = 0; j < sw.length; j++) say.add(i + j);
  }
  const sel = S.sel.line === ln.id;
  const editing = S.sel.editing === ln.id;
  const isStale = stale.includes(ln.id);
  const wav = `/f/${S.pid}/build/${part.id}/vo/${ln.id}.wav`;
  const text = editing
    ? `<textarea data-linetext="${ln.id}" rows="2">${esc(ln.text)}</textarea>`
    : toks.map((t, i) => {
        const c = clean(t);
        const cls = ["w", words.includes(c) ? "a" : model.includes(c) ? "v" : "", anc.includes(c) ? "anc" : "", lost.length && i === 0 ? "" : "", say.has(i) ? "say" : ""].join(" ");
        return `<span class="${cls}" data-word="${esc(c)}" title="${anc.includes(c) ? "Animation is pinned to this word" : "Click: highlight amber → violet → off"}">${esc(t)}</span>`;
      }).join(" ") + (lost.length ? ` <span class="chip r" title="The animation was pinned to these words; it now falls back to the middle of the line">⚠ ${esc(lost.join(", "))} missing</span>` : "");
  const dur = li ? li.line.length : partInfo(part.id)?.lengths?.[ln.id] ?? null;
  return `<div class="line ${sel ? "sel" : ""}" data-selline="${ln.id}" data-part="${part.id}">
    <span class="id">${esc(ln.id)}</span><div class="tx">${text}</div>
    <div class="acts">
      ${isStale ? `<span class="chip a" title="Text or voice settings changed">NEW VOICE</span>` : `<span class="ico" data-play="${wav}" title="Play">▶</span>`}
      <span class="ico" data-act="edit" data-line="${ln.id}" title="Edit text">${editing ? "✓" : "✎"}</span>
      <span class="ico ${anchors[ln.id] ? "dis" : ""}" data-act="delLine" data-line="${ln.id}" data-part="${part.id}" title="${anchors[ln.id] ? "The animation uses this line, so it can't be deleted (edit it instead)" : "Delete line"}" style="${anchors[ln.id] ? "opacity:.3" : ""}">✕</span>
    </div>
    <span class="t ${isStale ? "amber" : ""}">${dur && !isStale ? dur.toFixed(1) + "s" : "~" + estSeconds(ln.text).toFixed(1) + "s"}</span>
  </div>`;
}

function viewScript() {
  const P = S.p, anchors = anchoredLines(), stale = staleVoice();
  const total = totalSeconds();
  const sl = S.sel.line && P.parts.flatMap((p) => p.lines).find((l) => l.id === S.sel.line);
  const errs = (S.insp?.parts || []).filter((p) => p.error && !p.error.startsWith("no voice"));
  const miss = missingAnchors();
  const voices = S.insp?.voices || [P.voice.name];
  return header("STEP 1", "Script &amp; Voice", `
    <span class="btn ${stale.length ? "primary" : "dis"}" data-act="voiceAll">▶ Voice changed lines (${stale.length})</span>`) + `
  <div style="display:grid;grid-template-columns:1fr 360px;gap:18px;align-items:start">
    <div style="display:flex;flex-direction:column;gap:12px;min-width:0">
      <div class="panel" style="padding:12px 16px">
        <h3 style="margin-bottom:8px">Total duration <span class="r"><b style="color:var(--paper);font:700 15px Inter">${fmt(total)}</b>
          <span class="smoke">· target ${fmt(P.target_seconds).replace(/\.\d$/, "")} · Shorts max 3:00</span>
          ${total > 180 ? `<span class="chip r">TOO LONG</span>` : ""}</span></h3>
        <div class="dur">${P.parts.map((p, i) => `<div style="width:${(100 * partSeconds(p) / total).toFixed(2)}%;background:${PART_COLORS[i % 8]}" title="${esc(p.title)}">${i + 1} · ${esc(p.title.toUpperCase())} ${partSeconds(p).toFixed(1)}s</div>`).join("")}</div>
      </div>
      ${errs.length || miss.length || S.insp?.error ? `<div class="panel" style="border-color:#ff6b6b66">
        ${S.insp?.error ? `<div class="err">${esc(S.insp.error)}</div>` : ""}
        ${errs.map((p) => `<div class="err">${esc(p.id)}: ${esc(p.error)}</div>`).join("")}
        ${miss.map((m) => `<div class="err">⚠ Line ${esc(m.line)} no longer says “${esc(m.word)}”. The animation was timed to that word; it now uses the middle of the line. Put the word back, or ask Claude to re-time the scene.</div>`).join("")}
      </div>` : ""}
      ${P.parts.map((part, pi) => {
        const open = !S.collapsed[part.id];
        const info = partInfo(part.id);
        const st = (info?.stale_voice || []).length;
        return `<div class="part ${open ? "open" : ""}">
          <div class="ph" data-act="togglePart" data-part="${part.id}">
            <span class="chip a">PART ${pi + 1}</span>
            ${open ? `<input data-bind="parts.${pi}.title" value="${esc(part.title)}" data-stop>` : `<b>${esc(part.title)}</b>`}
            <span class="smoke">${part.lines.length} line${part.lines.length === 1 ? "" : "s"}</span>
            <div class="r">${st ? `<span class="chip a">${st} NEED VOICE</span>` : `<span class="chip g">VOICE ✓</span>`}
              <span class="mono">${partSeconds(part).toFixed(1)} s</span><span class="smoke">${open ? "▾" : "▸"}</span></div>
          </div>
          ${open ? part.lines.map((ln) => lineHtml(part, ln, anchors, info?.stale_voice || [])).join("") +
            `<div style="padding:8px 14px"><span class="btn sm" data-act="addLine" data-part="${part.id}">＋ Add line</span></div>` : ""}
        </div>`;
      }).join("")}
    </div>

    <div style="display:flex;flex-direction:column;gap:14px;position:sticky;top:0">
      <div class="panel">
        <h3>Voice</h3>
        <div class="field"><label>Narrator</label><div class="row"><select data-bind="voice.name" data-rerender>${voices.map((v) => `<option ${v === P.voice.name ? "selected" : ""}>${v}</option>`).join("")}</select>
          <span class="btn sm" data-act="previewVoice">▶ Hear</span></div></div>
        ${rng("Speed", "voice.speed", 0.7, 1.4, 0.01, (v) => v.toFixed(2) + "×")}
        ${rng("Pause between lines", "voice.gap", 0, 1.5, 0.05, (v) => v.toFixed(2) + " s")}
        <div class="muted">Changing the narrator or speed means every line needs a new voice.</div>
      </div>
      ${sl ? `<div class="panel"><h3>Line ${esc(sl.id)}</h3>
        ${rng("Extra pause before this line", `voice.pauses.${sl.id}`, 0, 2, 0.05, (v) => v.toFixed(2) + " s", 0)}
        <div class="row"><span class="btn sm" data-act="voiceLine" data-line="${sl.id}">⟳ New voice for ${esc(sl.id)}</span>
          ${anchors[sl.id] ? `<span class="muted">Pinned words: ${esc(anchors[sl.id].join(", ") || "line start")}</span>` : ""}</div></div>` : ""}
      <div class="panel">
        <h3>Caption words <span class="r"><span class="amber">● your words</span> · <span class="violet">● the model</span></span></h3>
        <div class="muted" style="margin-bottom:8px">Click a word in the script to highlight it. Underlined words are where the animation is pinned.</div>
        <div class="chips" style="margin-bottom:6px">${P.words.map((w, i) => `<span class="chip a">${esc(w)}<span class="x" data-act="rmWord" data-list="words" data-i="${i}">✕</span></span>`).join("")}</div>
        <div class="chips">${P.model.map((w, i) => `<span class="chip v">${esc(w)}<span class="x" data-act="rmWord" data-list="model" data-i="${i}">✕</span></span>`).join("")}</div>
      </div>
      <div class="panel">
        <h3>Say it → show it</h3>
        <table>${P.display.map((d, i) => `<tr><td><input data-bind="display.${i}.0" value="${esc(d[0])}"></td><td style="width:100px"><input data-bind="display.${i}.1" value="${esc(d[1])}"></td>
          <td style="width:24px"><span class="x" data-act="rmDisplay" data-i="${i}" style="cursor:pointer">✕</span></td></tr>`).join("")}
          <tr><td colspan="3"><span class="btn sm" data-act="addDisplay">＋ Add</span></td></tr></table>
      </div>
    </div>
  </div>`;
}

function rng(label, path, min, max, step, show, dflt = null, cls = "") {
  const v = getp(path) ?? dflt ?? min;
  const id = "o" + path.replace(/\W/g, "_");
  return `<div class="field"><label>${label} <b id="${id}">${show(+v)}</b></label>
    <input type="range" class="${cls}" min="${min}" max="${max}" step="${step}" value="${v}" data-bind="${path}" data-num data-out="${id}" data-show="${esc(show.toString())}" style="--p:${(100 * (v - min) / (max - min)).toFixed(1)}%"></div>`;
}

// ---------------------------------------------------------------- scenes & timeline
function timeline() {
  const parts = (S.insp?.parts || []).filter((p) => p.ready);
  const total = S.insp?.total || 1;
  const X = (t) => `${(100 * t / total).toFixed(3)}%`;
  const W = (a, b) => `${Math.max(0.2, 100 * (b - a) / total).toFixed(3)}%`;
  const lines = parts.flatMap((p) => p.lines.map((l) => ({ ...l, part: p.id, abs: p.offset + l.start })));
  const lineStart = Object.fromEntries(lines.map((l) => [l.id, l.abs]));
  const shots = shotTimes(lines);
  const words = new Set(S.p.words.map(clean)), model = new Set(S.p.model.map(clean));
  const sfxGain = S.p.audio.sfx || {};
  const ticks = [];
  for (let t = 0; t <= total; t += total > 150 ? 20 : 10) ticks.push(t);
  const caps = lines.flatMap((l) => l.words.filter((w) => words.has(clean(w[2])) || model.has(clean(w[2])))
    .map((w) => ({ t: l.abs + w[0] - l.start + l.start, w: w[2], c: words.has(clean(w[2])) ? "a" : "v" })));
  const pinned = parts.flatMap((p) => Object.entries(p.anchors || {}).flatMap(([lid, ws]) => {
    const l = p.lines.find((x) => x.id === lid);
    if (!l) return [];
    return (ws.length ? ws : [null]).map((w) => {
      const hit = w && l.words.find((x) => clean(x[2]) === clean(w));
      return { t: p.offset + (hit ? hit[0] : l.start), w: w || lid, ok: !w || !!hit };
    });
  }));
  return `<div class="tl" id="tl">
    <div class="ruler">${ticks.map((t) => `<span style="left:${X(t)}">${fmt(t).replace(/\.\d$/, "")}</span>`).join("")}</div>
    <div class="trk"><b>PARTS</b><div class="lane" data-lane>${parts.map((p, i) => `<div class="clip" style="left:${X(p.offset)};width:${W(p.offset, p.offset + p.duration)};background:${PART_COLORS[i % 8]}">${i + 1} ${esc((S.p.parts.find((x) => x.id === p.id)?.title || p.id).toUpperCase())}</div>`).join("")}</div></div>
    <div class="trk"><b>SHOTS</b><div class="lane" data-lane>${shots.map((s, i) => `<div class="clip ${S.sel.shot === s.n ? "sel" : ""}" style="left:${X(s.t)};width:${W(s.t, shots[i + 1]?.t ?? total)};background:${S.sel.shot === s.n ? "var(--amber)" : "#2a2834"};color:${S.sel.shot === s.n ? "var(--ink)" : "var(--smoke)"}" data-shot="${s.n}">${s.n}</div>`).join("")}</div></div>
    <div class="trk"><b>VOICE</b><div class="lane" data-lane>${lines.map((l) => `<div class="clip" style="left:${X(l.abs)};width:${W(l.abs, l.abs + l.length)};background:#8b6cff55;color:var(--paper)" title="${esc(S.p.parts.flatMap((p) => p.lines).find((x) => x.id === l.id)?.text || "")}">${l.id}</div>`).join("")}</div></div>
    <div class="trk"><b>HIGHLIGHTS</b><div class="lane" data-lane>${caps.map((c) => `<div class="mk" style="left:${X(c.t)};background:${c.c === "a" ? "var(--amber)" : "var(--violet)"};width:5px;top:9px;bottom:9px" title="${esc(c.w)}"></div>`).join("")}</div></div>
    <div class="trk"><b>PINNED</b><div class="lane" data-lane>${pinned.map((a) => `<div class="mk" style="left:${X(a.t)};background:${a.ok ? "var(--amber)" : "var(--red)"}" title="animation pinned to “${esc(a.w)}”${a.ok ? "" : " (missing)"}"></div>`).join("")}</div></div>
    <div class="trk"><b>SOUND FX</b><div class="lane" data-lane>${parts.flatMap((p) => p.sfx.map(([t, k, g]) => `<div class="mk ${(sfxGain[k] ?? 1) === 0 ? "muted" : ""}" style="left:${X(p.offset + t)};opacity:${Math.min(1, 0.35 + g * (sfxGain[k] ?? 1))}" title="${esc(k)} · ${g}"></div>`)).join("")}</div></div>
    <div class="trk"><b>MUSIC</b><div class="lane" data-lane>${parts.flatMap((p) => p.music.map(([a, b, k, g], j) => `<div class="clip" style="left:${X(p.offset + a)};width:${W(p.offset + a, p.offset + Math.min(b, p.duration))};background:${j % 2 ? "#3b2f55" : "#2b2840"};color:#b6a4ff;font-size:9px;${j % 2 ? "top:16px;bottom:2px" : "top:2px;bottom:16px"}">${esc(k)}</div>`)).join("")}</div></div>
    <div class="head" id="head" style="left:calc(124px + (100% - 138px) * ${(S.sel.t / total).toFixed(4)})"><i>${fmt(S.sel.t)}</i></div>
  </div>`;
}

function shotTimes(lines) {
  // shots on the same line share it: spread them evenly across the line
  const byLine = {};
  (S.p.shots || []).forEach((s) => (byLine[s.line] = byLine[s.line] || []).push(s));
  const L = Object.fromEntries(lines.map((l) => [l.id, l]));
  return (S.p.shots || []).map((s) => {
    const l = L[s.line], grp = byLine[s.line];
    return { ...s, t: l ? l.abs + (l.length * grp.indexOf(s)) / grp.length : 0 };
  }).sort((a, b) => a.t - b.t || a.n - b.n);
}
function allLines() {
  return (S.insp?.parts || []).filter((p) => p.ready).flatMap((p) => p.lines.map((l) => ({ ...l, part: p.id, abs: p.offset + l.start })));
}

function partAt(t) {
  const parts = (S.insp?.parts || []).filter((p) => p.ready);
  return parts.find((p) => t >= p.offset && t < p.offset + p.duration) || parts.at(-1);
}

function viewScenes() {
  if (!S.insp) return header("STEP 2", "Scenes &amp; Timeline") + `<div class="muted">Loading timeline…</div>`;
  const fileNames = (S.files?.files || []).map((f) => f.name);
  const vname = fileNames.includes("full_share.mp4") ? "full_share.mp4" : fileNames.includes("full.mp4") ? "full.mp4" : null;
  const pt = partAt(S.sel.t);
  const ptitle = pt && S.p.parts.find((x) => x.id === pt.id)?.title;
  const anyStale = (S.insp.parts || []).some((p) => p.video !== "final");
  const shot = (S.p.shots || []).find((s) => s.n === S.sel.shot);
  const shotIdx = (S.p.shots || []).indexOf(shot);
  const sfxKinds = pt ? [...new Set(pt.sfx.map((x) => x[1]))] : [];
  const bedKinds = pt ? [...new Set(pt.music.map((x) => x[2]))] : [];
  const capY = S.p.style.captions.y / 1920 * 100;
  return header("STEP 2", "Scenes &amp; Timeline", `
    <div class="seg" style="width:220px">${["draft", "final"].map((q) => `<div class="${S.quality === q ? "on" : ""}" data-quality="${q}">${q === "draft" ? "Draft · fast" : "Final"}</div>`).join("")}</div>
    ${pt ? `<span class="btn primary" data-act="renderPart" data-part="${pt.id}">◉ Render ${esc(pt.id)}</span>` : ""}`) + `
  <div class="scn">
    <div class="panel scroll" style="max-height:620px"><h3>Shots <span class="r smoke">${(S.p.shots || []).length}</span></h3>
      <div class="shots">${(S.p.shots || []).map((s) => `<div class="shot ${S.sel.shot === s.n ? "sel" : ""}" data-shot="${s.n}" style="background-image:url(/f/${S.pid}/${s.panel})"><span>${s.n}</span></div>`).join("")}</div>
      <span class="btn sm" data-act="storyboard" style="margin-top:10px">⟳ Redraw storyboard</span>
    </div>
    <div class="stage">
      <div class="phone">
        ${S.stillShown ? `<img src="${S.stillShown}" alt="">` : vname ? `<video id="player" src="/f/${S.pid}/out/${vname}" preload="auto" playsinline></video>` : `<div class="ph-msg">No video yet. Use “Frame here” to see a frame, or render a part.</div>`}
        ${S.safe ? `<div class="safe cap" style="top:${capY.toFixed(1)}%"><b>CAPTIONS</b></div><div class="safe" style="top:77.1%"><b>YOUTUBE BUTTONS · KEEP CLEAR</b></div>` : ""}
      </div>
      <div class="tools">
        <span class="btn sm" data-act="seek" data-d="-1">◀ 1s</span>
        <span class="btn sm primary" data-act="play" style="padding:5px 16px">${S.stillShown ? "▶ Video" : "▶ / ❚❚"}</span>
        <span class="btn sm" data-act="seek" data-d="1">1s ▶</span>
        <span class="mono smoke" id="tc" style="margin:0 6px;white-space:nowrap">${fmt(S.sel.t)} / ${fmt(S.insp.total)}</span>
        <span class="btn sm" data-act="frameHere">◉ Frame here</span>
        <span class="chip ${S.safe ? "g" : ""}" data-act="safe" style="cursor:pointer">SAFE ZONES</span>
      </div>
      ${vname && anyStale ? `<div class="muted amber">The video is older than your latest changes. Render to update it.</div>` : ""}
    </div>
    <div class="panel scroll" style="max-height:620px">
      ${shot ? `<h3>Shot ${shot.n} <span class="r"><span class="chip a">${esc(shot.line)}</span></span></h3>
        <div class="field"><label>What happens</label><textarea rows="3" data-bind="shots.${shotIdx}.action">${esc(shot.action)}</textarea></div>
        <div class="field"><label>Sound idea</label><textarea rows="2" data-bind="shots.${shotIdx}.sound">${esc(shot.sound)}</textarea></div>` : ""}
      ${pt ? `<h3 style="margin-top:6px">${esc(pt.id)} · ${esc(ptitle || "")} <span class="r">${videoChip(pt.video)}</span></h3>
        <div class="row" style="flex-wrap:wrap;gap:6px;margin-bottom:12px">
          <span class="btn sm" data-act="renderPart" data-part="${pt.id}">◉ Render part</span>
          <span class="btn sm" data-act="soundOnly" data-part="${pt.id}">♪ Hear sound mix</span>
          ${pt.has_video ? `<span class="btn sm" data-open="/f/${S.pid}/build/${pt.id}/video.mp4">▶ Part video</span>` : ""}</div>
        <h3>Sound effects in this part <span class="r smoke">volume · 0 = off</span></h3>
        <div class="kv">${sfxKinds.map((k) => sfxRow("audio.sfx." + k, k)).join("")}</div>
        <h3 style="margin-top:12px">Music</h3>
        <div class="kv">${bedKinds.map((k) => sfxRow("audio.beds." + k, k)).join("")}</div>
        <div class="muted" style="margin-top:8px">Volumes apply to every part that uses the same sound.</div>` : ""}
    </div>
  </div>
  ${timeline()}`;
}
function sfxRow(path, label) {
  const v = getp(path) ?? 1;
  const id = "o" + path.replace(/\W/g, "_");
  return `<span>${esc(label.replace(/_/g, " "))}</span><input type="range" min="0" max="2" step="0.05" value="${v}" data-bind="${path}" data-num data-out="${id}" data-show="(v)=>v.toFixed(2)" style="--p:${50 * v}%"><b id="${id}" class="mono" style="font-size:11px">${(+v).toFixed(2)}</b>`;
}
function videoChip(v) {
  return { final: `<span class="chip g">FINAL ✓</span>`, draft: `<span class="chip v">DRAFT</span>`, stale: `<span class="chip a">OUT OF DATE</span>`, none: `<span class="chip">NOT RENDERED</span>` }[v] || "";
}

// ---------------------------------------------------------------- style & sound
const ROLES = { amber: "your words, the prompt", violet: "the model, noise, maths", paper: "main text", smoke: "labels, figures",
  carbon: "background", ink: "deepest black", card: "cards" };
function viewStyle() {
  const P = S.p, st = P.style;
  const kinds = [...new Set((S.insp?.parts || []).flatMap((p) => (p.sfx || []).map((x) => x[1])))].sort();
  const beds = [...new Set((S.insp?.parts || []).flatMap((p) => (p.music || []).map((x) => x[2])))].sort();
  const parts = (S.insp?.parts || []).filter((p) => p.ready);
  if (!S.styleAt || (parts.length && !parts.some((p) => p.id === S.styleAt.part))) S.styleAt = { part: parts[1]?.id || parts[0]?.id || "part1", t: 8 };
  const pv = S.styleAt;
  const show = (k) => (v) => v.toFixed(2) + "×";
  return header("STEP 3", "Style &amp; Sound", `<span class="btn" data-open-text="STYLE_GUIDE.md">📄 Style guide</span>`) + `
  <div style="display:grid;grid-template-columns:340px 1fr 360px;gap:16px;align-items:start">
    <div style="display:flex;flex-direction:column;gap:14px">
      <div class="panel"><h3>Palette <span class="r smoke">colour = meaning</span></h3>
        ${Object.entries(st.palette).map(([k, v]) => `<div class="sw"><input type="color" value="${v}" data-bind="style.palette.${k}" data-upper><div><b>${k[0].toUpperCase() + k.slice(1)}</b><small>${ROLES[k] || ""}</small></div><span class="mono smoke" style="font-size:11px">${v}</span></div>`).join("")}
      </div>
      <div class="panel"><h3>Type</h3>
        <div style="font:900 21px Inter;padding:4px 0">Inter Display Black <span class="muted">titles</span></div>
        <div class="serif amber" style="font-size:22px;padding:4px 0">Noto Serif italic <span class="muted" style="font-style:normal">emphasis</span></div>
        <div class="mono" style="font-weight:700;padding:4px 0">NOTO SANS MONO <span class="muted">labels</span></div>
      </div>
      <div class="panel"><h3>Rules</h3>
        <div class="row" style="margin-bottom:8px"><div class="toggle ${st.vector_only ? "on" : ""}" data-toggle="style.vector_only"></div>Vector art only, no AI-generated images</div>
        <div class="muted">Every picture is drawn in code (art.py), at any size.</div>
      </div>
    </div>
    <div style="display:flex;flex-direction:column;gap:14px">
      <div class="panel"><h3>Captions <span class="r"><span class="chip a">DENOISE-IN</span></span></h3>
        <div class="grid2">
          ${rng("Size", "style.captions.size", 56, 110, 1, (v) => v + " px")}
          ${rng("Max words per caption", "style.captions.max_words", 1, 5, 1, (v) => "≤ " + v)}
          ${rng("Height on screen (y)", "style.captions.y", 1100, 1480, 5, (v) => v + " px")}
        </div>
        <div class="muted">Keep the height at 1480 or less so the YouTube buttons never cover captions.</div>
      </div>
      <div class="panel"><h3>Finish (post effects) <span class="r smoke">1.0 = as designed</span></h3>
        <div class="grid2">
          ${rng("Glow (amber/violet only)", "style.post.bloom", 0, 2, 0.05, show())}
          ${rng("Film grain", "style.post.grain", 0, 2, 0.05, show())}
          ${rng("Colour fringing", "style.post.ca", 0, 2, 0.05, show(), null, "v")}
          ${rng("Glitch strength", "style.post.glitch", 0, 2, 0.05, show(), null, "v")}
          ${rng("Motion blur samples (final)", "style.post.samples", 1, 5, 1, (v) => String(v), null, "v")}
        </div>
        <h3 style="margin-top:6px">Preview a frame with these settings</h3>
        <div class="row"><select data-styleat="part" style="width:120px">${parts.map((p) => `<option ${p.id === pv.part ? "selected" : ""}>${p.id}</option>`).join("")}</select>
          <input type="number" step="0.1" min="0" value="${pv.t}" data-styleat="t" style="width:90px"><span class="muted">s</span>
          <span class="btn sm primary" data-act="stylePreview">◉ Render frame</span></div>
        <div class="row" style="margin-top:12px;gap:10px;align-items:flex-start">${S.preview.slice(0, 2).map((p, i) => `<div style="flex:1"><div class="muted">${i ? "Before" : "Latest"} · ${esc(p.label)}</div><img src="${p.url}" style="width:100%;border-radius:10px;margin-top:4px;cursor:pointer" data-open="${p.url}"></div>`).join("") || `<div class="muted">No preview yet.</div>`}</div>
      </div>
      <div class="panel"><h3>Vector art library <span class="r smoke">${S.art.filter((a) => !a.name.startsWith("step_") && a.name !== "sheet.png").length} drawings</span></h3>
        <div class="lib">${S.art.filter((a) => !a.name.startsWith("step_") && a.name !== "sheet.png").map((a) => `<div class="art" data-open="${a.url}"><div style="background-image:url(${a.url})"></div><p>${esc(a.name.replace(/\.png$/, "").replace(/_/g, " "))}</p></div>`).join("") || `<div class="muted">Drawings appear here after the first render.</div>`}</div>
        <div class="muted" style="margin-top:8px">New drawings are code: ask Claude, e.g. “draw a lighthouse in a storm in art.py”.</div>
      </div>
    </div>
    <div style="display:flex;flex-direction:column;gap:14px">
      <div class="panel"><h3>Sound mix</h3>
        ${rng("Voice level", "audio.voice", 0.3, 1.2, 0.01, (v) => v.toFixed(2))}
        ${rng("Music level", "audio.music", 0, 1, 0.01, (v) => v.toFixed(2))}
        ${rng("Sound effects level", "audio.fx", 0, 1, 0.01, (v) => v.toFixed(2))}
        ${rng("Loudness target", "audio.lufs", -20, -9, 0.5, (v) => v.toFixed(1) + " LUFS")}
        <h3 style="margin-top:6px">Music beds</h3><div class="kv">${beds.map((k) => sfxRow("audio.beds." + k, k)).join("")}</div>
        <h3 style="margin-top:12px">Sound effects <span class="r smoke">0 = off</span></h3><div class="kv">${kinds.map((k) => sfxRow("audio.sfx." + k, k)).join("")}</div>
      </div>
    </div>
  </div>`;
}

// ---------------------------------------------------------------- render & publish
function viewRender() {
  const P = S.p, parts = S.insp?.parts || [];
  const files = S.files?.files || [];
  const L = S.files?.loudness;
  const f = (n) => files.find((x) => x.name === n);
  const full = f("full.mp4");
  const total = S.insp?.total || totalSeconds();
  const newest = Math.max(0, ...parts.map((p) => p.video === "final" ? 1 : 0));
  const checks = [
    [total <= 180, `Length under 3:00 (${fmt(total)})`],
    [!staleVoice().length, staleVoice().length ? `${staleVoice().length} line(s) need a new voice` : "Every line has its voice"],
    [!missingAnchors().length && !parts.some((p) => p.error), missingAnchors().length ? "Some scenes lost the word they were timed to" : "All scenes find their timing words"],
    [parts.length && parts.every((p) => p.video === "final"), parts.every((p) => p.video === "final") ? "All parts rendered in final quality" : "Some parts are out of date or drafts"],
    [!!full, full ? "Full video exists" : "No full video yet"],
    [!!f("thumb_short.png"), "Phone cover (thumbnail) made"],
    [P.style.captions.y <= 1480, "Captions above the YouTube buttons"],
    [!!P.style.vector_only, "All pictures are vector drawings"],
  ];
  const jobs = S.jobs.filter((j) => j.project === S.pid).slice(0, 8);
  const post = P.posting;
  return header("STEP 4", "Render &amp; Publish", `
    <div class="seg" style="width:300px">${["draft", "final"].map((q) => `<div class="${S.quality === q ? "on" : ""}" data-quality="${q}">${q === "draft" ? "Draft · fast (1 sample)" : "Final · motion blur"}</div>`).join("")}</div>
    <span class="btn primary" data-act="renderFull">◉ Render full video</span>`) + `
  <div style="display:grid;grid-template-columns:1fr 1fr 400px;gap:16px;align-items:start">
    <div style="display:flex;flex-direction:column;gap:14px;min-width:0">
      <div class="panel"><h3>Parts <span class="r smoke">only out-of-date parts re-render</span></h3>
        ${parts.map((p, i) => `<div class="job"><span class="chip a">PART ${i + 1}</span><div><b>${esc(P.parts.find((x) => x.id === p.id)?.title || p.id)}</b>
          <small> · ${p.ready ? Math.round(p.duration * 30) + " frames · " + p.duration.toFixed(1) + " s" : esc(p.error || "")}</small></div>
          <span class="st">${videoChip(p.video)}<span class="btn sm" data-act="renderPart" data-part="${p.id}">◉</span></span></div>`).join("")}
        <div class="row" style="margin-top:10px;gap:8px;flex-wrap:wrap"><span class="btn sm" data-act="thumbs">⟳ Thumbnails</span><span class="btn sm" data-act="storyboard">⟳ Storyboard</span><span class="btn sm" data-act="rerenderFull">⟳ Re-render everything</span></div>
      </div>
      <div class="panel"><h3>Jobs</h3>
        ${jobs.length ? jobs.map((j) => `<div style="padding:8px 0;border-top:1px solid var(--line)">
          <div class="row"><b style="font-size:13px">${esc(j.label)}</b><span class="sp" style="flex:1"></span>
            <span class="chip ${j.status === "done" ? "g" : j.status === "failed" ? "r" : j.status === "running" ? "v" : ""}">${j.status.toUpperCase()}</span>
            ${["running", "queued"].includes(j.status) ? `<span class="btn sm danger" data-act="cancel" data-job="${j.id}">Stop</span>` : ""}
            <span class="btn sm" data-act="log" data-job="${j.id}">Log</span></div>
          ${j.progress ? `<div class="pbar"><i style="width:${(100 * j.progress.done / j.progress.total).toFixed(1)}%"></i></div><small class="muted">${j.progress.part}: ${j.progress.done}/${j.progress.total} frames</small>` : ""}
          ${j.status === "failed" ? `<div class="log">${esc(j.log.join("\n"))}</div>` : ""}</div>`).join("") : `<div class="muted">Nothing rendered in this session yet.</div>`}
      </div>
      <div class="panel"><h3>Version history <span class="r smoke">every save keeps a copy</span></h3><div id="hist" class="muted">${histHtml()}</div></div>
    </div>
    <div style="display:flex;flex-direction:column;gap:14px;min-width:0">
      <div class="panel"><h3>Sound check ${L ? `<span class="r"><span class="chip ${Math.abs(L.lufs - P.audio.lufs) < 1 ? "g" : "a"}">${L.lufs.toFixed(1)} LUFS</span> <span class="chip ${L.peak <= -1 ? "g" : "a"}">PEAK ${L.peak.toFixed(1)} dB</span></span>` : ""}</h3>
        ${L ? `<div class="muted">Measured on full.mp4 (${fmt(L.duration)}). Target ${P.audio.lufs} LUFS, peak under −1 dB.</div>` : `<div class="muted">Render the full video to measure it.</div>`}</div>
      <div class="panel"><h3>Files</h3>
        <div class="outs">${["youtube_upload_cover.mp4", "full.mp4", "full_share.mp4", "thumb_short.png", "thumb_wide.png", "storyboard_1.png"].map(f).filter(Boolean).map((x) => `
          <div class="out" data-open="${x.url}"><div class="th" style="${x.name.endsWith(".png") ? `background-image:url(${x.url}?v=${x.mtime})` : ""}">${x.name.endsWith(".mp4") ? "▶" : ""}</div>
          <div style="min-width:0"><b>${esc(x.name)}</b><small>${(x.size / 1e6).toFixed(1)} MB</small><br><small>${new Date(x.mtime * 1000).toLocaleString()}</small></div></div>`).join("") || `<div class="muted">No files yet.</div>`}</div>
        <div class="muted" style="margin-top:8px">Upload <b>youtube_upload_cover.mp4</b>: it ends on the thumbnail so you can pick it as the phone cover.</div></div>
      <div class="panel"><h3>Before you post</h3>${checks.map(([ok, t]) => `<div class="check"><i class="${ok ? "" : "w"}">${ok ? "✓" : "!"}</i>${esc(t)}</div>`).join("")}</div>
      <div class="panel"><h3>Save to GitHub</h3>
        <div class="muted" style="margin-bottom:8px">Saves the script, settings and code. Videos are left out: they can be rebuilt from the code.</div>
        <div class="row"><input id="commitMsg" placeholder="What changed? (optional)"><span class="btn primary" data-act="gitSave">⎇ Save</span></div>
        <div class="muted" style="margin-top:6px">${S.git.changed ? `${S.git.changed.length} changed file(s) on ${esc(S.git.branch)}` : ""}</div></div>
    </div>
    <div class="panel" style="min-width:0"><h3>Posting kit <span class="r"><div class="toggle ${P.posted ? "on" : ""}" data-toggle="posted" title="Mark as posted"></div><span class="smoke">posted</span></span></h3>
      <div class="field"><label>Title <b class="${post.title.length > 100 ? "err" : "green"}">${post.title.length} / 100</b></label><input data-bind="posting.title" value="${esc(post.title)}" data-rerender></div>
      <div class="field"><label>Other titles</label>${post.titles.map((t, i) => `<div class="row" style="margin-bottom:5px"><input data-bind="posting.titles.${i}" value="${esc(t)}"><span class="btn sm" data-act="useTitle" data-i="${i}">Use</span></div>`).join("")}</div>
      <div class="field"><label>Description <span class="x" data-copy="posting.description" style="cursor:pointer">⧉ copy</span></label><textarea rows="8" data-bind="posting.description">${esc(post.description)}</textarea></div>
      <div class="field"><label>Tags <span class="x" data-copy="posting.tags" style="cursor:pointer">⧉ copy</span></label><textarea rows="3" data-bind="posting.tags">${esc(post.tags)}</textarea></div>
      <div class="field"><label>Pinned comment <span class="x" data-copy="posting.pinned" style="cursor:pointer">⧉ copy</span></label><textarea rows="3" data-bind="posting.pinned">${esc(post.pinned)}</textarea></div>
      <div class="field"><label>Upload settings</label><textarea rows="4" data-bind="posting.settings">${esc(post.settings)}</textarea></div>
    </div>
  </div>`;
}
function histHtml() {
  if (!S.hist) { loadHist(); return "Loading…"; }
  if (!S.hist.length) return "No earlier versions yet.";
  return S.hist.slice(0, 12).map((h) => `<div class="row" style="justify-content:space-between;padding:4px 0;border-top:1px solid var(--line)"><span>${esc(h.when)}</span><span class="btn sm" data-act="restore" data-h="${h.id}">Restore</span></div>`).join("");
}
async function loadHist() { try { S.hist = await api(`/api/p/${S.pid}/history`); } catch (e) { S.hist = []; } safeRender(); }

// ---------------------------------------------------------------- events
function wire() {
  updateSaved();
  const v = $("#player");
  if (v) {
    v.addEventListener("timeupdate", () => { S.sel.t = v.currentTime; moveHead(); });
    if (Math.abs(v.currentTime - S.sel.t) > 0.3) v.addEventListener("loadedmetadata", () => { v.currentTime = S.sel.t; }, { once: true });
  }
}
function moveHead() {
  const h = $("#head"), total = S.insp?.total || 1;
  if (h) { h.style.left = `calc(124px + (100% - 138px) * ${(S.sel.t / total).toFixed(4)})`; h.querySelector("i").textContent = fmt(S.sel.t); }
  const tc = $("#tc");
  if (tc) tc.textContent = `${fmt(S.sel.t)} / ${fmt(total)}`;
}
function seekTo(t) {
  S.sel.t = Math.max(0, Math.min(t, S.insp?.total || 0));
  const v = $("#player");
  if (v) v.currentTime = S.sel.t;
  moveHead();
}

document.addEventListener("input", (e) => {
  const el = e.target;
  if (el.dataset.nv) { S.newVideo[el.dataset.nv] = el.type === "range" ? +el.value : el.value; if (el.dataset.out) $("#" + el.dataset.out).textContent = el.dataset.nv === "target" ? fmt(+el.value).replace(/\.\d$/, "") : el.value; return; }
  if (el.dataset.styleat) { S.styleAt[el.dataset.styleat] = el.dataset.styleat === "t" ? +el.value : el.value; return; }
  if (el.dataset.linetext) { setLineText(el.dataset.linetext, el.value); return; }
  const path = el.dataset.bind;
  if (!path) return;
  let val = el.value;
  if (el.dataset.num !== undefined) val = +val;
  if (el.dataset.upper !== undefined) val = val.toUpperCase();
  setp(path, val);
  if (el.type === "range") {
    el.style.setProperty("--p", `${(100 * (el.value - el.min) / (el.max - el.min)).toFixed(1)}%`);
    if (el.dataset.out) { const fn = eval(el.dataset.show); $("#" + el.dataset.out).textContent = fn(+val); }
  }
  changed(el.dataset.rerender !== undefined && el.tagName === "SELECT");
});
document.addEventListener("change", (e) => {
  if (e.target.dataset.rerender !== undefined) render();
});

function setLineText(id, text) {
  for (const p of S.p.parts) for (const l of p.lines) if (l.id === id) l.text = text.replace(/\s+/g, " ").trim();
  changed();
}
function nextLineId(part) {
  const all = S.p.parts.flatMap((p) => p.lines.map((l) => l.id));
  const prefix = (part.lines[0]?.id.match(/^[A-Za-z]+/) || ["L"])[0];
  let n = part.lines.length + 1;
  while (all.includes(prefix + n)) n++;
  return prefix + n;
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && e.target.dataset.linetext) { e.preventDefault(); e.target.blur(); S.sel.editing = null; render(); }
  if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); clearTimeout(saveTimer); save(); }
});

document.addEventListener("click", async (e) => {
  const t = e.target.closest("[data-act],[data-go],[data-play],[data-open],[data-shot],[data-word],[data-selline],[data-quality],[data-toggle],[data-nvset],[data-copy],[data-lane],[data-open-text]");
  if (!t) return;
  if (t.dataset.stop !== undefined || e.target.dataset.stop !== undefined) return;
  const d = t.dataset;
  if (d.go) { location.hash = d.go; return; }
  if (d.play) { playAudio(d.play); return; }
  if (d.open) { openModal(d.open); return; }
  if (d.openText) { openText(d.openText); return; }
  if (d.copy) { navigator.clipboard.writeText(getp(d.copy)).then(() => toast("Copied")); return; }
  if (d.nvset) { S.newVideo[d.nvset] = d.v; render(); return; }
  if (d.quality) { S.quality = d.quality; localStorage.setItem("quality", d.quality); render(); return; }
  if (d.toggle) { setp(d.toggle, !getp(d.toggle)); changed(true); return; }
  if (d.lane !== undefined) {
    const r = t.getBoundingClientRect();
    S.stillShown = null;
    const shotEl = e.target.closest("[data-shot]");
    if (shotEl) { selectShot(+shotEl.dataset.shot); return; }
    const tt = (e.clientX - r.left) / r.width * (S.insp?.total || 0);
    if (!$("#player")) { S.sel.t = tt; render(); } else seekTo(tt);
    return;
  }
  if (d.shot) { selectShot(+d.shot); return; }
  if (d.word && !d.act) {
    e.stopPropagation();
    const w = d.word, A = S.p.words, M = S.p.model;
    if (A.includes(w)) { A.splice(A.indexOf(w), 1); M.push(w); }
    else if (M.includes(w)) M.splice(M.indexOf(w), 1);
    else A.push(w);
    A.sort(); M.sort();
    changed(true);
    return;
  }
  if (d.selline && !d.act) { if (S.sel.line !== d.selline) { S.sel.line = d.selline; render(); } return; }
  e.stopPropagation();
  const act = d.act;
  const P = S.p;
  if (act === "togglePart") { if (e.target.tagName === "INPUT") return; S.collapsed[d.part] = !S.collapsed[d.part]; render(); }
  else if (act === "edit") { S.sel.line = d.line; S.sel.editing = S.sel.editing === d.line ? null : d.line; render(); if (S.sel.editing) { const ta = $(`[data-linetext="${d.line}"]`); ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length); } }
  else if (act === "addLine") {
    const part = P.parts.find((p) => p.id === d.part);
    const id = nextLineId(part);
    part.lines.push({ id, text: "Write the new line here." });
    S.sel.line = id; S.sel.editing = id;
    changed(true);
    const ta = $(`[data-linetext="${id}"]`); if (ta) { ta.focus(); ta.select(); }
  }
  else if (act === "delLine") {
    if (anchoredLines()[d.line]) return toast("The animation uses this line. Edit it instead of deleting it.", true);
    if (!confirm(`Delete line ${d.line}?`)) return;
    const part = P.parts.find((p) => p.id === d.part);
    part.lines = part.lines.filter((l) => l.id !== d.line);
    changed(true);
  }
  else if (act === "rmWord") { P[d.list].splice(+d.i, 1); changed(true); }
  else if (act === "addDisplay") { P.display.push(["spoken words", "shown"]); changed(true); }
  else if (act === "rmDisplay") { P.display.splice(+d.i, 1); changed(true); }
  else if (act === "voiceAll") job({ kind: "voice_all" });
  else if (act === "voiceLine") { const li = P.parts.find((p) => p.lines.some((l) => l.id === d.line)); job({ kind: "voice", part: li.id, lines: [d.line] }); }
  else if (act === "previewVoice") {
    const text = (S.sel.line && P.parts.flatMap((p) => p.lines).find((l) => l.id === S.sel.line)?.text) || P.parts[0].lines[0].text;
    job({ kind: "preview", voice: P.voice.name, speed: P.voice.speed, text });
  }
  else if (act === "renderPart") job({ kind: "render_part", part: d.part, draft: S.quality === "draft" });
  else if (act === "renderFull") job({ kind: "render_full", draft: S.quality === "draft" });
  else if (act === "rerenderFull") { if (confirm("Re-render every part from scratch? This takes a while.")) job({ kind: "render_full", draft: S.quality === "draft", rerender: true }); }
  else if (act === "soundOnly") job({ kind: "audio", part: d.part });
  else if (act === "thumbs") job({ kind: "thumbs" });
  else if (act === "storyboard") job({ kind: "storyboard" });
  else if (act === "frameHere") {
    const pt = partAt(S.sel.t);
    if (!pt) return toast("No part here yet", true);
    const local = Math.max(0, S.sel.t - pt.offset);
    job({ kind: "still", part: pt.id, times: [+local.toFixed(2)], t_abs: S.sel.t, draft: true });
  }
  else if (act === "stylePreview") job({ kind: "still", part: S.styleAt.part, times: [+S.styleAt.t], draft: true });
  else if (act === "play") {
    if (S.stillShown) { S.stillShown = null; render(); return; }
    const v = $("#player"); if (!v) return toast("No video yet. Render first.", true);
    v.paused ? v.play() : v.pause();
  }
  else if (act === "seek") { S.stillShown = null; if (!$("#player")) { S.sel.t = Math.max(0, S.sel.t + +d.d); render(); } else seekTo(S.sel.t + +d.d); }
  else if (act === "safe") { S.safe = !S.safe; render(); }
  else if (act === "cancel") { await api(`/api/jobs/${d.job}/cancel`, { method: "POST" }); poll(); }
  else if (act === "log") { const j = await api(`/api/jobs/${d.job}`); openModal(null, `<h3>${esc(j.label)}</h3><div class="log" style="max-height:70vh;width:760px">${esc(j.log.join("\n") || "(no output)")}</div>`); }
  else if (act === "useTitle") { P.posting.title = P.posting.titles[+d.i]; changed(true); }
  else if (act === "restore") {
    if (!confirm("Go back to this version? Your current version is kept in the history too.")) return;
    await api(`/api/p/${S.pid}/history/${d.h}`, { method: "POST" });
    S.hist = null; await loadProject(S.pid); toast("Restored");
  }
  else if (act === "gitSave") {
    t.classList.add("dis");
    try { const r = await api(`/api/p/${S.pid}/save`, { method: "POST", body: { message: $("#commitMsg").value } }); toast(r.note, !r.ok); }
    catch (err) { toast(err.message, true); }
    t.classList.remove("dis"); refreshGit();
  }
  else if (act === "newVideo") {
    const nv = S.newVideo;
    if (!nv.topic.trim()) return toast("Write a topic first", true);
    try { const r = await api("/api/projects", { method: "POST", body: nv }); S.newVideo = null; location.hash = `#/p/${r.id}/script`; refreshProjects(); }
    catch (err) { toast(err.message, true); }
  }
});

function selectShot(n) {
  S.sel.shot = n;
  S.stillShown = null;
  const s = shotTimes(allLines()).find((x) => x.n === n);
  if (s) S.sel.t = s.t + 0.05;
  render();
}

function openModal(url, html) {
  const m = document.createElement("div");
  m.className = "modal";
  const isVid = url && /\.mp4|\.wav/.test(url);
  m.innerHTML = `<div>${html || (isVid ? `<video src="${url}" controls autoplay playsinline></video>` : `<img src="${url}">`)}
    ${url ? `<div class="row" style="margin-top:10px"><a class="btn sm" href="${url}" download>⬇ Download</a></div>` : ""}</div>`;
  m.addEventListener("click", (e) => { if (e.target === m) m.remove(); });
  document.body.appendChild(m);
}
async function openText(name) {
  const r = await fetch(`/f/${S.pid}/${name}`);
  openModal(null, `<pre class="log" style="max-height:75vh;width:800px">${esc(await r.text())}</pre>`);
}

// ---------------------------------------------------------------- routing
async function route() {
  const h = location.hash.replace(/^#\/?/, "");
  S.route = h ? h.split("/") : [];
  S.stillShown = null;
  if (S.route[0] === "p" && S.route[1]) {
    if (S.pid !== S.route[1] || !S.p) { S.hist = null; await loadProject(S.route[1]).catch((e) => { toast(e.message, true); location.hash = "#/"; }); return; }
    if (S.route[2] === "render") { S.hist = null; loadFiles(); refreshGit(); }
  } else refreshProjects();
  render();
}
window.addEventListener("hashchange", route);

(async function start() {
  await Promise.all([refreshProjects(), refreshGit()]);
  route();
  poll();
  setInterval(refreshGit, 30000);
})();
