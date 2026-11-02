import sys, os; sys.path.insert(0, "src")
from concurrent.futures import ThreadPoolExecutor
from recraft import generate, download
from items import PAINT, ISO, GROUPS, SCENES
jobs = []
for g, items in GROUPS.items():
    os.makedirs(f"raw/{g}", exist_ok=True)
    for name, desc in items:
        jobs.append((g, name, f"{desc}. {PAINT}. {ISO}", "1:1"))
os.makedirs("raw/scenes", exist_ok=True)
for name, desc in SCENES:
    jobs.append(("scenes", name, f"{desc}. {PAINT}, full illustrated scene with soft painted background, no text, no border", "3:4"))
def run(j):
    g, name, prompt, size = j
    if os.path.exists(f"raw/{g}/{name}_b.png"): return name, 0
    urls, cr = generate(prompt, model="recraftv4_1_flash", size=size, n=2)
    for i, u in enumerate(urls): download(u, f"raw/{g}/{name}_{'ab'[i]}.png")
    return name, cr or 0
total = 0
with ThreadPoolExecutor(5) as ex:
    for name, cr in ex.map(run, jobs): total += cr
print("jobs", len(jobs), "credits", total)
