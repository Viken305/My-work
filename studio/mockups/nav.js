// Shared sidebar for the mockups; <body data-page="script"> highlights the current step.
(function () {
  const page = document.body.dataset.page;
  const items = [
    ["projects", "⌂", "Projects", ""],
    ["script", "1", "Script & Voice", "✓"],
    ["scenes", "2", "Scenes & Timeline", "✓"],
    ["style", "3", "Style & Art", "✓"],
    ["render", "4", "Render & Publish", ""],
  ];
  const links = items.map(([id, n, name, tick]) =>
    `<a class="${id === page ? "on" : ""}"><i>${n}</i>${name}<span class="tick">${id === page ? "" : tick}</span></a>`).join("");
  document.body.insertAdjacentHTML("afterbegin", `
    <nav>
      <div class="brand"><div class="logo"></div><div><b>BrighterMinds</b><span>VIDEO STUDIO</span></div></div>
      ${page === "projects" ? "" : `<div class="proj"><small>PROJECT</small><div>How AI Draws From Nothing</div></div>`}
      ${links}
      <div class="grow"></div>
      <div class="git">GitHub · viken305/my-work<br>branch <b>claude/…yc4rv9</b><br>code saved ✓ · MP4s skipped</div>
    </nav>`);
})();
