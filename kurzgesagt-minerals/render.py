"""Renders any part, or the whole film with one continuous soundtrack.

  python3 render.py part2 --still 3,10,20   # check frames -> build/part2/stills
  python3 render.py part2                   # -> out/part2.mp4 (master) + out/part2_share.mp4
  python3 render.py full                    # all parts -> out/full.mp4 + out/full_share.mp4
Narration clips must exist first:  python3 voiceover.py partN
"""
import importlib, os, subprocess, sys
from multiprocessing import Pool

import skia

import audio
from engine import FPS, H, HERE, W, finish

PARTS = ["part1", "part2", "part3", "part4", "part5", "part6"]
OUT = os.path.join(HERE, "out")
_MOD = None


def build_dir(name):
    return os.path.join(HERE, "build", name)


def frame(mod, t):
    s = skia.Surface(W, H)
    mod.draw_frame(s.getCanvas(), t)
    return finish(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType), t)


def _init(name):
    global _MOD
    _MOD = importlib.import_module(name)


def _job(i):
    return frame(_MOD, i / FPS).tobytes()


def encode(src, dst, crf):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", dst], check=True)


def render_video(name):
    """Silent master video for one part -> build/<part>/video.mp4"""
    mod = importlib.import_module(name)
    os.makedirs(build_dir(name), exist_ok=True)
    out = os.path.join(build_dir(name), "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n = int(round(mod.DURATION * FPS))
    with Pool(os.cpu_count(), initializer=_init, initargs=(name,)) as pool:
        for k, buf in enumerate(pool.imap(_job, range(n), chunksize=4)):
            ff.stdin.write(buf)
            if k % 150 == 0:
                print(f"{name}: frame {k}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    return out


def vo_clips(name, mod, offset=0.0):
    return [(offset + t, os.path.join(build_dir(name), "vo", f"{key}.wav")) for key, t in mod.VO.items()]


def mux(video, wav, out):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)


def render_part(name):
    mod = importlib.import_module(name)
    wav = os.path.join(build_dir(name), "mix.wav")
    os.makedirs(build_dir(name), exist_ok=True)
    audio.render_mix(wav, mod.DURATION, vo_clips(name, mod), mod.sfx_events(), mod.MUSIC)
    os.makedirs(OUT, exist_ok=True)
    master = os.path.join(OUT, f"{name}.mp4")
    mux(render_video(name), wav, master)
    encode(master, os.path.join(OUT, f"{name}_share.mp4"), 28)
    print(master)


def render_full(rerender=False):
    clips, events, chords, pl, rises, offset = [], [], [], [], [], 0.0
    lst = os.path.join(HERE, "build", "full_list.txt")
    os.makedirs(os.path.dirname(lst), exist_ok=True)
    with open(lst, "w") as f:
        for name in PARTS:
            mod = importlib.import_module(name)
            video = os.path.join(build_dir(name), "video.mp4")
            if rerender or not os.path.exists(video):
                render_video(name)
            f.write(f"file '{video}'\n")
            clips += vo_clips(name, mod, offset)
            events += [(offset + t, k, g) for t, k, g in mod.sfx_events()]
            m = mod.MUSIC
            chords += [(offset + t, r, iv) for t, r, iv in m["chords"]]
            pl += [(offset + a, offset + b) for a, b in m["plucks"]]
            rises += [(offset + a, offset + b) for a, b in m["rises"]]
            offset += mod.DURATION
    music = dict(chords=chords, plucks=pl, bpm=96, rises=rises)
    wav = os.path.join(HERE, "build", "full_mix.wav")
    audio.render_mix(wav, offset, clips, events, music)
    video = os.path.join(HERE, "build", "full_video.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video], check=True)
    master = os.path.join(OUT, "full.mp4")
    mux(video, wav, master)
    encode(master, os.path.join(OUT, "full_share.mp4"), 28)
    print(master, f"{offset:.1f}s")


def stills(name, times):
    from PIL import Image
    mod = importlib.import_module(name)
    d = os.path.join(build_dir(name), "stills")
    os.makedirs(d, exist_ok=True)
    for ts in times:
        p = os.path.join(d, f"t{ts:05.2f}.png")
        Image.fromarray(frame(mod, ts)).save(p)
        print(p)


def main(argv):
    name = argv[0]
    if "--still" in argv:
        stills(name, [float(x) for x in argv[argv.index("--still") + 1].split(",")])
    elif name == "full":
        render_full("--rerender" in argv)
    else:
        render_part(name)


if __name__ == "__main__":
    main(sys.argv[1:])
