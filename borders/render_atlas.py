"""Render "Why Borders Are Shaped the Way They Are".

  python3 render.py --still 3,10.5,40     -> build/stills/tXX.XX.png
  python3 render.py sheet                 -> build/sheet.png (one frame per shot)
  python3 render.py full                  -> out/full.mp4 + out/full_share.mp4
"""
import os, subprocess, sys
from multiprocessing import Pool

from PIL import Image

import film_atlas as film
from film_atlas import CUTS, FPS, L, S, TOTAL, E, w

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD, OUT = os.path.join(HERE, "build"), os.path.join(HERE, "out")


def sfx_events():
    ev = [(0.1, "paper_whoosh", 0.35)]
    for k, ph in (("H2", "wiggle"), ("H2", "straight"), ("H2", "strange")):
        ev.append((w(k, ph), "marker", 0.55))
    ev += [(S("H3") - 0.25, "paper_slap", 0.4)]
    for name, s, e in CUTS[1:]:                                   # a page turn when the section changes
        prev = film.SPEC[CUTS[[c[0] for c in CUTS].index(name) - 1][0]]
        if prev[1] != film.SPEC[name][1]:
            ev.append((s - 0.15, "paper_whoosh", 0.45))
    ev += [(w("N2", "rio") - 0.1, "pencil_long", 0.5), (w("N3", "ridges") - 0.2, "pencil", 0.5),
           (w("N3", "pyrenees"), "marker", 0.4), (w("N4", "see") - 0.05, "stamp", 0.55), (w("N4", "cross") - 0.05, "stamp", 0.6),
           (S("S1") - 0.1, "ruler", 0.6), (w("S1", "drawn") - 0.1, "pencil_long", 0.6),
           (w("S2", "eighteen") - 0.05, "stamp", 0.55), (w("S2", "forty") - 0.1, "pencil", 0.55), (E("S2") - 0.4, "pencil", 0.4),
           (w("S3", "split") - 0.1, "pencil_long", 0.45), (w("S3", "straight"), "ruler", 0.5), (w("S3", "hundreds"), "marker", 0.4),
           (S("W1") - 0.3, "paper_whoosh", 0.4), (S("W1") + 0.1, "pencil", 0.4), (w("W1", "deals") - 0.05, "stamp", 0.7),
           (w("W2", "caprivi"), "marker", 0.45), (w("W2", "zambezi") - 0.3, "pencil", 0.35), (w("W2", "but") - 0.2, "pencil", 0.45),
           (w("W2", "falls") - 0.1, "stamp", 0.6), (w("W3", "wakhan") - 0.1, "marker", 0.5),
           (w("W3", "british") - 0.15, "pencil", 0.4), (w("W3", "russian") - 0.15, "pencil", 0.4)]
    ts, te = S("B1") - 0.2, w("B1", "deals", end=True)
    for i in range(0, len(film.BAARLE), 2):
        ev.append((ts + (te - ts) * i / len(film.BAARLE), "pop", 0.25))
    ev += [(w("B1", x) - 0.05, "pop", 0.35) for x in ("cafes", "gardens", "homes")]
    ev += [(S("B2") - 0.3, "pencil", 0.45), (w("B2", "door", end=True), "marker", 0.4),
           (w("B3", "rulers") - 0.1, "pencil", 0.4), (w("B3", "deals"), "marker", 0.4), (w("B3", "accidents"), "marker", 0.35)]
    return ev


def vo_clips():
    out = []
    for k, (t0, _, _) in L.items():
        out.append((t0, os.path.join(BUILD, film.LINE_PART[k], "vo", f"{k}.wav")))
    return out


def _job(i):
    return film.frame(i / FPS).tobytes()


def render_video(path):
    n = int(round(TOTAL * FPS))
    film.warm()
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{film.W}x{film.H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for i, b in enumerate(pool.imap(_job, range(n), chunksize=4)):
            p.stdin.write(b)
            if i % 300 == 0:
                print(f"  frame {i}/{n}", flush=True)
    p.stdin.close()
    p.wait()


def main(argv):
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    if argv and argv[0] == "--still":
        d = os.path.join(BUILD, "stills")
        os.makedirs(d, exist_ok=True)
        for t in (float(x) for x in argv[1].split(",")):
            Image.fromarray(film.frame(t)).save(os.path.join(d, f"t{t:05.2f}.png"))
        print(d)
    elif argv and argv[0] == "sheet":
        ts = [s + min(e - s - 0.1, max(1.2, (e - s) * 0.8)) for _, s, e in CUTS]
        ims = [Image.fromarray(film.frame(t)).resize((360, 640), Image.LANCZOS) for t in ts]
        sheet = Image.new("RGB", (360 * 5, 640 * 3), (243, 236, 222))
        for i, im in enumerate(ims):
            sheet.paste(im, ((i % 5) * 360, (i // 5) * 640))
        sheet.save(os.path.join(BUILD, "sheet.png"))
        print([round(t, 2) for t in ts])
    elif argv and argv[0] == "full":
        import audio
        video = os.path.join(BUILD, "full_video.mp4")
        render_video(video)
        wav = os.path.join(BUILD, "full_mix.wav")
        audio.render_mix(wav, TOTAL, vo_clips(), sfx_events(), dict(beds=[(0.0, TOTAL, "atlas", 0.55)]))
        master = os.path.join(OUT, "full.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                        "-shortest", master], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", master, "-c:v", "libx264", "-preset", "slow", "-crf", "24",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", os.path.join(OUT, "full_share.mp4")], check=True)
        print(master, f"{TOTAL:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1:])
