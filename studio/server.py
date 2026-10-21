"""BrighterMinds Video Studio: the dashboard server.

  python3 studio/server.py            -> open http://localhost:8765
  python3 studio/server.py --port 9000

Standard library only. Every folder of the repo with a project.json is an editable video project; the dashboard edits
that file and runs the project's own tools (voiceover.py, render.py, thumbnails.py, storyboard.py) as background jobs,
one at a time, with their output streamed into the job log.
"""
import argparse, datetime, json, mimetypes, os, re, shutil, subprocess, sys, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

STUDIO = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(STUDIO)
APP = os.path.join(STUDIO, "app")
PY = sys.executable
HISTORY_KEEP = 40


# ---------------------------------------------------------------- projects
def project_dir(pid):
    if not re.fullmatch(r"[\w.-]+", pid or ""):
        raise KeyError(pid)
    d = os.path.join(REPO, pid)
    if not os.path.isfile(os.path.join(d, "project.json")):
        raise KeyError(pid)
    return d


def read_project(pid):
    return json.load(open(os.path.join(project_dir(pid), "project.json")))


def save_project(pid, data):
    """Write project.json (keeping a timestamped copy of the previous version) and refresh SHORTS_POST.md."""
    d = project_dir(pid)
    path = os.path.join(d, "project.json")
    hist = os.path.join(d, "build", "_history")
    os.makedirs(hist, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy(path, os.path.join(hist, f"{stamp}.json"))
    for old in sorted(os.listdir(hist))[:-HISTORY_KEEP]:
        os.remove(os.path.join(hist, old))
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)
    write_post(d, data)


def write_post(d, p):
    post = p.get("posting")
    if not post:
        return
    titles = "\n".join(f"- {t}" + ("  ← recommended" if t == post.get("title") else "") for t in post.get("titles", []))
    text = (f"# Posting kit: {p.get('title', '')}\n\n**Title (pick one)**\n{titles}\n\n**Description**\n{post.get('description', '')}\n\n"
            f"**Tags**\n{post.get('tags', '')}\n\n**Pinned comment**\n{post.get('pinned', '')}\n\n**Settings**\n{post.get('settings', '')}\n")
    open(os.path.join(d, "SHORTS_POST.md"), "w").write(text)


def history(pid):
    hist = os.path.join(project_dir(pid), "build", "_history")
    if not os.path.isdir(hist):
        return []
    return [dict(id=f[:-5], when=datetime.datetime.strptime(f[:-5], "%Y%m%d-%H%M%S").strftime("%b %d, %H:%M:%S"))
            for f in sorted(os.listdir(hist), reverse=True) if f.endswith(".json")]


_INSPECT = {}


def inspect(pid, fresh=False):
    """Run the project's inspect_parts.py (a fresh process sees the saved project.json)."""
    d = project_dir(pid)
    key = _inputs_mtime(d)
    hit = _INSPECT.get(pid)
    if hit and hit[0] == key and not fresh:
        return hit[1]
    r = subprocess.run([PY, "inspect_parts.py"], cwd=d, capture_output=True, text=True, timeout=120)
    if r.returncode:
        res = dict(error=r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "inspect failed", parts=[], total=0)
    else:
        res = json.loads(r.stdout)
    _INSPECT[pid] = (key, res)
    return res


def _inputs_mtime(d):
    m = 0.0
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in ("out", "__pycache__", "_history", "stills", "_preview")]
        for f in files:
            if f.endswith((".py", ".json", ".wav", ".mp4")):
                m = max(m, os.path.getmtime(os.path.join(root, f)))
    return m


def list_projects():
    out = []
    for name in sorted(os.listdir(REPO)):
        d = os.path.join(REPO, name)
        if name.startswith((".", "studio")) or not os.path.isdir(d):
            continue
        if os.path.isfile(os.path.join(d, "project.json")):
            p = json.load(open(os.path.join(d, "project.json")))
            try:
                info = inspect(name)
            except Exception:
                info = {}
            out.append(dict(id=name, title=p.get("title", name), editable=True, format=p.get("format", "9:16"),
                            total=info.get("total"), stages=stages(d, p, info), posted=p.get("posted", False),
                            thumb=f"/f/{name}/out/thumb_short.png" if os.path.exists(os.path.join(d, "out", "thumb_short.png")) else None,
                            mtime=os.path.getmtime(os.path.join(d, "project.json"))))
        elif any(f.endswith(".py") for f in os.listdir(d)):
            out.append(dict(id=name, title=name.replace("-", " ").title(), editable=False,
                            mtime=max(os.path.getmtime(os.path.join(d, f)) for f in os.listdir(d))))
    return sorted(out, key=lambda x: (not x["editable"], -x["mtime"]))


ENGINE = ["kit.py", "film.py", "captions.py", "art.py", "timing.py", "script.py", "project.py", "voiceover.py", "render.py",
          "audio.py", "inspect_parts.py"]


def new_project(spec):
    """A new video folder: the engine of the newest studio project plus a project.json with the same look and voice,
    an empty script outline and the posting kit to fill in. The animation (partN.py) is written later, in code."""
    topic = (spec.get("topic") or "").strip()
    if not topic:
        raise ValueError("topic is empty")
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:40] or "video"
    pid, n = slug, 2
    while os.path.exists(os.path.join(REPO, pid)):
        pid, n = f"{slug}-{n}", n + 1
    src = next((x["id"] for x in list_projects() if x["editable"]), None)
    if not src:
        raise ValueError("no studio project to copy the engine from")
    s = project_dir(src)
    d = os.path.join(REPO, pid)
    os.makedirs(d)
    for f in ENGINE:
        if os.path.exists(os.path.join(s, f)):
            shutil.copy(os.path.join(s, f), d)
    base = read_project(src)
    nparts = max(1, min(8, int(spec.get("parts", 5))))
    letters = "HABCDEFG"
    p = dict(base)
    p.update(title=topic.rstrip("?"), format=spec.get("format", "9:16"), target_seconds=int(spec.get("target", 100)),
             parts=[dict(id=f"part{i + 1}", title="Hook" if i == 0 else f"Part {i + 1}",
                         lines=[dict(id=f"{letters[i]}1", text="Write the first line of this part here.")]) for i in range(nparts)],
             display=[], words=[], model=[], shots=[], posted=False,
             posting=dict(titles=[topic], title=topic, description="", tags="", pinned="", settings=base.get("posting", {}).get("settings", "")))
    p["voice"] = dict(base["voice"], name=spec.get("voice") or base["voice"]["name"], pauses={}, first_by_part={})
    p["audio"] = dict(base["audio"], sfx={}, beds={})
    with open(os.path.join(d, "project.json"), "w") as f:
        json.dump(p, f, indent=1, ensure_ascii=False)
    return dict(ok=True, id=pid)


def stages(d, p, info):
    """Pipeline bar: script, voice, scenes, render, post -> 'done' / 'todo' / 'work'."""
    parts = info.get("parts") or []
    voice = "done" if parts and not any(x.get("stale_voice") for x in parts) else "work"
    scenes = "done" if parts and all(x.get("ready") and not x.get("missing_anchors") for x in parts) else "work"
    vids = [x.get("video") for x in parts]
    full = os.path.join(d, "out", "full.mp4")
    if parts and all(v == "final" for v in vids) and os.path.exists(full):
        render = "done"
    else:
        render = "work" if any(v in ("final", "draft") for v in vids) else "todo"
    return dict(script="done" if p.get("parts") else "todo", voice=voice if parts else "todo", scenes=scenes if parts else "todo",
                render=render, post="done" if p.get("posted") else ("work" if render == "done" else "todo"))


# ---------------------------------------------------------------- files
def out_files(pid, sub="out"):
    d = project_dir(pid)
    res = []
    if not re.fullmatch(r"out(/\w+)?", sub):
        raise ValueError("bad folder")
    for sub in (sub,):
        base = os.path.join(d, sub)
        if not os.path.isdir(base):
            continue
        for f in sorted(os.listdir(base)):
            path = os.path.join(base, f)
            if os.path.isfile(path):
                res.append(dict(name=f, url=f"/f/{pid}/{sub}/{f}", size=os.path.getsize(path),
                                mtime=os.path.getmtime(path)))
    return res


_LOUD = {}


def loudness(pid, name="full.mp4"):
    path = os.path.join(project_dir(pid), "out", name)
    if not os.path.exists(path):
        return None
    m = os.path.getmtime(path)
    if _LOUD.get(path, (0,))[0] == m:
        return _LOUD[path][1]
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex("{"):])
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    res = dict(lufs=float(j["input_i"]), peak=float(j["input_tp"]),
               duration=int(dur[1]) * 3600 + int(dur[2]) * 60 + float(dur[3]) if dur else None)
    _LOUD[path] = (m, res)
    return res


# ---------------------------------------------------------------- jobs
JOBS, _QUEUE, _LOCK = [], [], threading.Condition()


def job_command(pid, spec):
    """(label, argv, env) for a job request from the dashboard."""
    kind, part = spec.get("kind"), spec.get("part")
    env = {}
    if spec.get("draft"):
        env["STUDIO_SAMPLES"] = "1"
    if kind == "voice":
        argv = ["voiceover.py", part] + (["--lines", ",".join(spec["lines"])] if spec.get("lines") else [])
        return f"Voice {part}" + (f" ({', '.join(spec['lines'])})" if spec.get("lines") else ""), argv, env
    if kind == "voice_all":
        parts = [x["id"] for x in read_project(pid)["parts"]]
        return "Voice all changed lines", ["-c", "import voiceover as v\nfor p in %r: v.voice_part(p)" % parts], env
    if kind == "preview":
        return f"Preview voice {spec['voice']}", ["voiceover.py", "--preview", spec["voice"], str(spec["speed"]), spec["text"]], env
    if kind == "still":
        times = ",".join(f"{float(t):.2f}" for t in spec["times"])
        return f"Still {part} @ {times}s", ["render.py", part, "--still", times], env
    if kind == "audio":
        return f"Sound mix {part}", ["render.py", part, "--audio"], env
    if kind == "render_part":
        return f"Render {part}" + (" (draft)" if env else ""), ["render.py", part], env
    if kind == "render_full":
        return "Render full video" + (" (draft)" if env else ""), ["render.py", "full"] + (["--rerender"] if spec.get("rerender") else []), env
    if kind == "thumbs":
        return "Thumbnails", ["thumbnails.py"], env
    if kind == "storyboard":
        return "Storyboard", ["storyboard.py"], env
    raise ValueError(f"unknown job kind {kind!r}")


def add_job(pid, spec):
    label, argv, env = job_command(pid, spec)
    job = dict(id=uuid.uuid4().hex[:8], project=pid, label=label, spec=spec, argv=argv, env=env, status="queued",
               progress=None, log=[], created=time.time(), started=None, ended=None, result=None)
    with _LOCK:
        JOBS.append(job)
        _QUEUE.append(job)
        _LOCK.notify()
    return job


def public(job, full_log=False):
    j = {k: v for k, v in job.items() if k not in ("argv", "env", "proc", "log")}
    j["log"] = job["log"] if full_log else job["log"][-6:]
    return j


def worker():
    while True:
        with _LOCK:
            while not _QUEUE:
                _LOCK.wait()
            job = _QUEUE.pop(0)
        if job["status"] == "cancelled":
            continue
        job.update(status="running", started=time.time())
        env = {**os.environ, **job["env"], "PYTHONUNBUFFERED": "1"}
        try:
            proc = subprocess.Popen([PY] + job["argv"], cwd=project_dir(job["project"]), env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, bufsize=1)
        except Exception as e:
            job.update(status="failed", ended=time.time(), log=[str(e)])
            continue
        job["proc"] = proc
        for line in proc.stdout:
            line = line.rstrip()
            if not line or "Fontconfig" in line:
                continue
            job["log"].append(line)
            del job["log"][:-400]
            m = re.search(r"(part\d+): frame (\d+)/(\d+)", line)
            if m:
                job["progress"] = dict(part=m[1], done=int(m[2]), total=int(m[3]))
            if line.endswith((".png", ".wav", ".mp4")) or ".mp4 " in line:
                job["result"] = line.split()[0]
        proc.wait()
        if job["status"] != "cancelled":
            job["status"] = "done" if proc.returncode == 0 else "failed"
        job["ended"] = time.time()
        job.pop("proc", None)
        _INSPECT.pop(job["project"], None)


def cancel(jid):
    for job in JOBS:
        if job["id"] == jid and job["status"] in ("queued", "running"):
            if job.get("proc"):
                _kill_tree(job["proc"].pid)
            job["status"] = "cancelled"
            return True
    return False


def _kill_tree(pid):
    """Stop a job and the render workers it started (only its own children, never this server)."""
    try:
        kids = subprocess.run(["pgrep", "-P", str(pid)], capture_output=True, text=True).stdout.split()
    except FileNotFoundError:
        kids = []
    for k in kids:
        _kill_tree(int(k))
    try:
        os.kill(pid, 15)
    except ProcessLookupError:
        pass


# ---------------------------------------------------------------- git
def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError((r.stderr or r.stdout).strip())
    return r.stdout.strip()


def git_status():
    try:
        branch = git("rev-parse", "--abbrev-ref", "HEAD")
        st = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True).stdout
        changed = [ln[3:] for ln in st.splitlines() if ln.strip()]
        ahead = git("rev-list", "--count", f"origin/{branch}..HEAD", check=False) or "?"
        remote = git("config", "--get", "remote.origin.url", check=False)
        repo = re.sub(r"^.*[:/]([^/]+/[^/]+?)(\.git)?$", r"\1", remote) if remote else ""
        return dict(branch=branch, changed=changed, ahead=ahead, repo=repo)
    except Exception as e:
        return dict(error=str(e))


def git_save(pid, message):
    """Commit the project's code and settings (videos are git-ignored) and push the current branch."""
    paths = [os.path.relpath(project_dir(pid), REPO), "studio"]
    git("add", "--", *paths)
    if not git("diff", "--cached", "--name-only"):
        return dict(ok=True, note="Nothing new to save")
    git("commit", "-m", message or f"Update {pid} from the studio")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    for wait in (0, 2, 4, 8, 16):
        time.sleep(wait)
        r = subprocess.run(["git", "push", "-u", "origin", branch], cwd=REPO, capture_output=True, text=True)
        if r.returncode == 0:
            return dict(ok=True, note=f"Saved and pushed to {branch}")
    return dict(ok=False, note="Committed locally; push failed: " + r.stderr.strip()[-300:])


# ---------------------------------------------------------------- http
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def do_PUT(self):
        self.route("PUT")

    def route(self, method):
        url = urlparse(self.path)
        parts = [unquote(x) for x in url.path.strip("/").split("/") if x]
        q = parse_qs(url.query)
        try:
            if not parts or parts[0] == "app":
                return self.static(os.path.join(APP, *(parts[1:] or ["index.html"])))
            if parts[0] == "f":
                return self.static(os.path.join(project_dir(parts[1]), *parts[2:]), root=project_dir(parts[1]))
            if parts[0] != "api":
                return self.send_json(dict(error="not found"), 404)
            return self.api(method, parts[1:], q)
        except KeyError as e:
            self.send_json(dict(error=f"not found: {e}"), 404)
        except (ValueError, RuntimeError) as e:
            self.send_json(dict(error=str(e)), 400)
        except BrokenPipeError:
            pass

    def api(self, method, p, q):
        if p == ["projects"]:
            if method == "POST":
                return self.send_json(new_project(self.body()))
            return self.send_json(list_projects())
        if p == ["jobs"]:
            return self.send_json([public(j) for j in JOBS[-30:]][::-1])
        if len(p) == 2 and p[0] == "jobs":
            return self.send_json(next(public(j, True) for j in JOBS if j["id"] == p[1]))
        if len(p) == 3 and p[0] == "jobs" and p[2] == "cancel" and method == "POST":
            return self.send_json(dict(ok=cancel(p[1])))
        if p == ["git"]:
            return self.send_json(git_status())
        if p[0] == "p" and len(p) >= 2:
            pid, rest = p[1], p[2:]
            if not rest:
                if method == "PUT":
                    save_project(pid, self.body())
                    return self.send_json(dict(ok=True))
                return self.send_json(read_project(pid))
            if rest == ["inspect"]:
                return self.send_json(inspect(pid, fresh="fresh" in q))
            if rest == ["files"]:
                sub = q.get("dir", ["out"])[0]
                if sub != "out":
                    return self.send_json(dict(files=out_files(pid, sub)))
                return self.send_json(dict(files=out_files(pid), loudness=loudness(pid)))
            if rest == ["history"]:
                return self.send_json(history(pid))
            if rest[0] == "history" and len(rest) == 2:
                path = os.path.join(project_dir(pid), "build", "_history", re.sub(r"[^\d-]", "", rest[1]) + ".json")
                if method == "POST":
                    save_project(pid, json.load(open(path)))
                    return self.send_json(dict(ok=True))
                return self.send_json(json.load(open(path)))
            if rest == ["jobs"] and method == "POST":
                return self.send_json(public(add_job(pid, self.body())))
            if rest == ["save"] and method == "POST":
                return self.send_json(git_save(pid, self.body().get("message")))
            if rest == ["stills"]:
                return self.send_json(stills(pid, q.get("part", [""])[0]))
        self.send_json(dict(error="unknown endpoint"), 404)

    def static(self, path, root=APP):
        path = os.path.realpath(path)
        if not path.startswith(os.path.realpath(root)) or not os.path.isfile(path):
            return self.send_json(dict(error="not found"), 404)
        size = os.path.getsize(path)
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        start, end = 0, size - 1
        rng = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
        if rng and (rng[1] or rng[2]):
            if rng[1]:
                start = int(rng[1])
                end = int(rng[2]) if rng[2] else end
            else:
                start = size - int(rng[2])
            end = min(end, size - 1)
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(left, 1 << 16))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)


def stills(pid, part):
    d = os.path.join(project_dir(pid), "build", part, "stills")
    if not re.fullmatch(r"\w+", part) or not os.path.isdir(d):
        return []
    return [dict(t=float(f[1:-4]), url=f"/f/{pid}/build/{part}/stills/{f}", mtime=os.path.getmtime(os.path.join(d, f)))
            for f in sorted(os.listdir(d)) if re.fullmatch(r"t[\d.]+\.png", f)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args()
    threading.Thread(target=worker, daemon=True).start()
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f"BrighterMinds Video Studio: http://localhost:{a.port}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
