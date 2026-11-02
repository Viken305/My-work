"""Small Recraft API helper: generate, crisp upscale, remove background."""
import os, sys, json, requests

API = "https://external.api.recraft.ai/v1"
HDR = {"Authorization": f"Bearer {os.environ['RECRAFT_API_TOKEN']}"}

def generate(prompt, model="recraftv4_1", size="1:1", n=1, extra=None):
    body = {"prompt": prompt, "model": model, "size": size, "n": n,
            "response_format": "url", "image_format": "png"}
    if extra: body.update(extra)
    r = requests.post(f"{API}/images/generations", headers=HDR, json=body, timeout=300)
    if r.status_code != 200: sys.exit(f"generate failed {r.status_code}: {r.text}")
    j = r.json()
    return [d["url"] for d in j["data"]], j.get("credits")

def _tool(endpoint, path):
    with open(path, "rb") as f:
        r = requests.post(f"{API}/images/{endpoint}", headers=HDR,
                          files={"file": f}, data={"response_format": "url", "image_format": "png"}, timeout=300)
    if r.status_code != 200: sys.exit(f"{endpoint} failed {r.status_code}: {r.text}")
    j = r.json()
    return j["image"]["url"], j.get("credits")

def crisp_upscale(path): return _tool("crispUpscale", path)
def remove_background(path): return _tool("removeBackground", path)

def download(url, path):
    r = requests.get(url, timeout=300); r.raise_for_status()
    open(path, "wb").write(r.content)

def generate_with_ref(prompt, ref_paths, model="recraftv4_1", size="1:1", n=1, style_match="flexible"):
    files = [("style_references", (os.path.basename(p), open(p, "rb"), "image/png")) for p in ref_paths]
    data = {"prompt": prompt, "model": model, "size": size, "n": str(n), "style_match": style_match,
            "response_format": "url", "image_format": "png"}
    r = requests.post(f"{API}/images/generations", headers=HDR, data=data, files=files, timeout=300)
    if r.status_code != 200: sys.exit(f"generate failed {r.status_code}: {r.text}")
    j = r.json()
    return [d["url"] for d in j["data"]], j.get("credits"), j.get("style_id")
